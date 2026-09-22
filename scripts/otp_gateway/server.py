from __future__ import annotations

import argparse
import hmac
import json
import os
import re
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


OTP_PATTERN = re.compile(r"^\d{4,12}$")
MAX_BODY_BYTES = 32 * 1024


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def mask_phone(phone: str) -> str:
    return phone


class CaptchaSourceError(RuntimeError):
    """Raised when the configured CAPTCHA source cannot provide a valid code."""


class CaptchaSource:
    def __init__(self, source_url: str, timeout_seconds: float = 5) -> None:
        self.source_url = source_url.strip()
        self.timeout_seconds = timeout_seconds

    @property
    def configured(self) -> bool:
        return bool(self.source_url)

    def fetch(self, phone: str) -> str:
        if not self.configured:
            raise CaptchaSourceError("captcha source is not configured")
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise CaptchaSourceError("captcha source URL must be an absolute HTTP(S) URL")
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["tel"] = phone
        source_url = urlunparse(parsed._replace(query=urlencode(query)))
        request = Request(source_url, headers={"Accept": "application/json, text/plain"})
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode(response.headers.get_content_charset() or "utf-8")
        except HTTPError as error:
            raise CaptchaSourceError(f"captcha source returned HTTP {error.code}") from error
        except (URLError, TimeoutError, UnicodeDecodeError) as error:
            raise CaptchaSourceError("captcha source request failed") from error
        code = self._extract_code(body)
        if code is None:
            raise CaptchaSourceError("captcha source response does not contain a valid code")
        return code

    @classmethod
    def _extract_code(cls, body: str) -> str | None:
        try:
            payload: Any = json.loads(body)
        except json.JSONDecodeError:
            payload = body
        if isinstance(payload, dict) and payload.get("success") is False:
            message = str(payload.get("message", "captcha source rejected the request")).strip()
            raise CaptchaSourceError(f"captcha source rejected the request: {message}")
        return cls._find_code(payload)

    @classmethod
    def _find_code(cls, value: Any) -> str | None:
        if isinstance(value, (str, int)):
            text = str(value).strip()
            if OTP_PATTERN.fullmatch(text):
                return text
            match = re.search(r"(?<!\d)(\d{4,12})(?!\d)", text)
            return match.group(1) if match else None
        if isinstance(value, dict):
            for key in ("mockCode", "captcha", "captchaCode", "verifyCode", "verificationCode"):
                if key in value:
                    code = cls._find_code(value[key])
                    if code:
                        return code
            for key in ("data", "result", "body"):
                if key in value:
                    code = cls._find_code(value[key])
                    if code:
                        return code
            return None
        if isinstance(value, list):
            for item in value:
                code = cls._find_code(item)
                if code:
                    return code
        return None


class OtpStore:
    def __init__(self, database_path: str | Path, ttl_seconds: int = 300) -> None:
        self.database_path = str(database_path)
        self.ttl_seconds = ttl_seconds
        self.lock = threading.RLock()
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS otp_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    account TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    code TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    expires_epoch REAL NOT NULL,
                    consumed_at TEXT,
                    UNIQUE(request_id, account)
                );
                CREATE INDEX IF NOT EXISTS idx_otp_lookup
                    ON otp_codes(account, request_id, phone, expires_epoch, consumed_at);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def put(
        self,
        *,
        request_id: str,
        account: str,
        phone: str,
        code: str,
        message: str | None,
    ) -> dict[str, Any]:
        created = utc_now()
        expires = created + timedelta(seconds=self.ttl_seconds)
        with self.lock, self._connection() as connection:
            try:
                cursor = connection.execute(
                    """
                    INSERT INTO otp_codes
                        (request_id, account, phone, code, message, created_at,
                         expires_at, expires_epoch)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        request_id,
                        account,
                        phone,
                        code,
                        message,
                        isoformat(created),
                        isoformat(expires),
                        expires.timestamp(),
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise ValueError("request_id already exists for this account") from error
            return {
                "id": cursor.lastrowid,
                "requestId": request_id,
                "account": account,
                "expiresAt": isoformat(expires),
            }

    def put_fetched_code(self, phone: str, code: str) -> None:
        with self.lock, self._connection() as connection:
            row = connection.execute(
                """
                SELECT code, expires_epoch
                FROM otp_codes
                WHERE phone = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (phone,),
            ).fetchone()
        if row is not None and row["code"] == code and row["expires_epoch"] > utc_now().timestamp():
            return
        self.put(
            request_id=uuid.uuid4().hex,
            account="",
            phone=phone,
            code=code,
            message="Fetched from captcha source",
        )

    def latest(
        self,
        *,
        account: str | None,
        request_id: str | None,
        phone: str | None,
    ) -> dict[str, Any] | None:
        with self.lock, self._connection() as connection:
            filters = ["consumed_at IS NULL", "expires_epoch > ?"]
            values: list[Any] = [utc_now().timestamp()]
            if account:
                filters.append("account = ?")
                values.append(account)
            if request_id:
                filters.append("request_id = ?")
                values.append(request_id)
            if phone:
                filters.append("phone = ?")
                values.append(phone)
            row = connection.execute(
                f"""
                SELECT id, request_id, account, phone, code, message,
                       created_at, expires_at, expires_epoch, consumed_at
                FROM otp_codes
                WHERE {' AND '.join(filters)}
                ORDER BY id DESC
                LIMIT 1
                """,
                values,
            ).fetchone()
            if row is None:
                return None
            return {
                "id": row["id"],
                "requestId": row["request_id"],
                "account": row["account"],
                "phone": mask_phone(row["phone"]),
                "code": row["code"],
                "message": row["message"],
                "createdAt": row["created_at"],
                "expireAt": row["expires_at"],
            }

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self.lock, self._connection() as connection:
            rows = connection.execute(
                """
                SELECT id, request_id, account, phone, code, message,
                       created_at, expires_at, expires_epoch, consumed_at
                FROM otp_codes
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [
                {
                    "id": row["id"],
                    "requestId": row["request_id"],
                    "account": row["account"],
                    "phone": mask_phone(row["phone"]),
                    "code": row["code"],
                    "message": row["message"],
                    "createdAt": row["created_at"],
                    "expireAt": row["expires_at"],
                    "status": (
                        "consumed"
                        if row["consumed_at"] is not None
                        else "expired"
                        if row["expires_epoch"] <= utc_now().timestamp()
                        else "available"
                    ),
                }
                for row in rows
            ]

    def consume(self, record_id: int) -> bool:
        with self.lock, self._connection() as connection:
            cursor = connection.execute(
                """
                UPDATE otp_codes
                SET consumed_at = ?
                WHERE id = ? AND consumed_at IS NULL AND expires_epoch > ?
                """,
                (isoformat(utc_now()), record_id, utc_now().timestamp()),
            )
            return cursor.rowcount == 1


class OtpRequestHandler(BaseHTTPRequestHandler):
    server_version = "OtpGateway/1.0"

    @property
    def gateway(self) -> "OtpGateway":
        return self.server  # type: ignore[return-value]

    def log_message(self, format_string: str, *args: Any) -> None:
        message = format_string % args
        if "code" not in message.lower() and "authorization" not in message.lower():
            super().log_message("%s", message)

    def _json_response(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _html_response(self, status: int, content: str) -> None:
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'")
        self.end_headers()
        self.wfile.write(encoded)

    def _error(self, status: int, message: str) -> None:
        self._json_response(status, {"error": message})

    def _authorized(self, expected_token: str) -> bool:
        header = self.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        return scheme.lower() == "bearer" and bool(token) and hmac.compare_digest(token, expected_token)

    def _read_access_allowed(self) -> bool:
        return not self.gateway.read_auth_required or self._authorized(self.gateway.read_token)

    def _read_json(self) -> dict[str, Any] | None:
        content_length = self.headers.get("Content-Length")
        try:
            length = int(content_length or "0")
        except ValueError:
            self._error(HTTPStatus.BAD_REQUEST, "invalid Content-Length")
            return None
        if length <= 0 or length > MAX_BODY_BYTES:
            self._error(HTTPStatus.BAD_REQUEST, "request body must be between 1 and 32768 bytes")
            return None
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._error(HTTPStatus.BAD_REQUEST, "request body must be valid JSON")
            return None
        if not isinstance(payload, dict):
            self._error(HTTPStatus.BAD_REQUEST, "request body must be a JSON object")
            return None
        return payload

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._html_response(HTTPStatus.OK, self.gateway.web_page)
            return
        if path == "/healthz":
            self._json_response(HTTPStatus.OK, {"status": "ok"})
            return
        if path not in {"/api/test/otp/latest", "/api/test/otp/recent"}:
            self._error(HTTPStatus.NOT_FOUND, "not found")
            return
        if not self._read_access_allowed():
            self._error(HTTPStatus.UNAUTHORIZED, "invalid read token")
            return
        query = parse_qs(urlparse(self.path).query)
        if path == "/api/test/otp/recent":
            try:
                limit = int(query.get("limit", ["50"])[0])
            except ValueError:
                self._error(HTTPStatus.BAD_REQUEST, "limit must be an integer")
                return
            self._json_response(HTTPStatus.OK, {"items": self.gateway.store.recent(limit)})
            return
        account = query.get("account", [""])[0].strip()
        request_id = query.get("requestId", [""])[0].strip() or None
        phone = query.get("phone", [""])[0].strip() or None
        if not phone:
            self._error(HTTPStatus.BAD_REQUEST, "phone is required")
            return
        if len(phone) > 32:
            self._error(HTTPStatus.BAD_REQUEST, "phone must be at most 32 characters")
            return
        if self.gateway.captcha_source.configured:
            try:
                code = self.gateway.captcha_source.fetch(phone)
            except CaptchaSourceError as error:
                self._error(HTTPStatus.BAD_GATEWAY, str(error))
                return
            self.gateway.store.put_fetched_code(phone, code)
        record = self.gateway.store.latest(account=account, request_id=request_id, phone=phone)
        if record is None:
            self._error(HTTPStatus.NOT_FOUND, "no available otp")
            return
        self._json_response(HTTPStatus.OK, record)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/test/otp":
            self._receive_otp()
            return
        if path == "/api/test/otp/consume":
            self._consume_otp()
            return
        self._error(HTTPStatus.NOT_FOUND, "not found")

    def _receive_otp(self) -> None:
        if self.gateway.ingest_auth_required and not self._authorized(self.gateway.ingest_token):
            self._error(HTTPStatus.UNAUTHORIZED, "invalid ingest token")
            return
        payload = self._read_json()
        if payload is None:
            return
        request_id = str(payload.get("requestId", "")).strip() or uuid.uuid4().hex
        account = str(payload.get("account", "")).strip()
        phone = str(payload.get("phone", "")).strip()
        code = str(payload.get("code", "")).strip()
        message = payload.get("message")
        if len(request_id) > 128:
            self._error(HTTPStatus.BAD_REQUEST, "requestId must be at most 128 characters")
            return
        if account and len(account) > 128:
            self._error(HTTPStatus.BAD_REQUEST, "account must be at most 128 characters")
            return
        if self.gateway.allowed_phones is not None and phone not in self.gateway.allowed_phones:
            self._error(HTTPStatus.FORBIDDEN, "phone is not allowed")
            return
        if not phone or len(phone) > 32:
            self._error(HTTPStatus.BAD_REQUEST, "phone is required and must be at most 32 characters")
            return
        if not OTP_PATTERN.fullmatch(code):
            self._error(HTTPStatus.BAD_REQUEST, "code must contain 4 to 12 digits")
            return
        if message is not None and (not isinstance(message, str) or len(message) > 2000):
            self._error(HTTPStatus.BAD_REQUEST, "message must be a string of at most 2000 characters")
            return
        try:
            result = self.gateway.store.put(
                request_id=request_id,
                account=account,
                phone=phone,
                code=code,
                message=message,
            )
        except ValueError as error:
            self._error(HTTPStatus.CONFLICT, str(error))
            return
        self._json_response(HTTPStatus.CREATED, result)

    def _consume_otp(self) -> None:
        if not self._read_access_allowed():
            self._error(HTTPStatus.UNAUTHORIZED, "invalid read token")
            return
        payload = self._read_json()
        if payload is None:
            return
        try:
            record_id = int(payload.get("id"))
        except (TypeError, ValueError):
            self._error(HTTPStatus.BAD_REQUEST, "id must be an integer")
            return
        if not self.gateway.store.consume(record_id):
            self._error(HTTPStatus.NOT_FOUND, "otp is missing, expired, or already consumed")
            return
        self._json_response(HTTPStatus.OK, {"consumed": True, "id": record_id})


class OtpGateway(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        store: OtpStore,
        ingest_token: str,
        read_token: str,
        allowed_phones: set[str] | None = None,
        read_auth_required: bool = False,
        ingest_auth_required: bool = False,
        captcha_source: CaptchaSource | None = None,
    ) -> None:
        super().__init__(address, OtpRequestHandler)
        self.store = store
        self.ingest_token = ingest_token
        self.read_token = read_token
        self.allowed_phones = allowed_phones
        self.read_auth_required = read_auth_required
        self.ingest_auth_required = ingest_auth_required
        self.captcha_source = captcha_source or CaptchaSource("")
        self.web_page = self._build_web_page()

    @staticmethod
    def _build_web_page() -> str:
        return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Swan OTP Gateway</title>
  <style>
    :root { --ink:#172033; --muted:#667085; --line:#e6e9ef; --bg:#f5f7fb; --card:#fff; --good:#087f5b; --good-weak:#e6fcf5; --warn:#ad6800; --warn-weak:#fff9db; --neutral-weak:#f1f3f8; --hover:#f8f9ff; }
    * { box-sizing:border-box; }
    body { margin:0; padding:18px 20px 28px; background:var(--bg); color:var(--ink); font:13px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }
    main { max-width:1240px; margin:0 auto; }
    .otp-head { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
    .otp-head h1 { margin:0; font-size:17px; font-weight:600; }
    .otp-head .meta { color:var(--muted); font-size:12px; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:12px; box-shadow:0 2px 10px rgba(23,32,51,.03); overflow:hidden; }
    table { width:100%; border-collapse:collapse; }
    th { padding:8px 12px; text-align:left; color:var(--muted); background:#fafbfc; font-size:12px; font-weight:600; border-bottom:1px solid var(--line); }
    td { padding:9px 12px; border-bottom:1px solid var(--line); font-size:13px; text-align:left; }
    tbody tr:last-child td { border-bottom:0; }
    tbody tr:hover { background:var(--hover); }
    code.otp { font-family:ui-monospace,Consolas,monospace; font-size:16px; font-weight:700; color:var(--ink); letter-spacing:2px; background:var(--neutral-weak); padding:3px 10px; border-radius:8px; }
    .rid { font-family:ui-monospace,Consolas,monospace; font-size:12px; color:var(--muted); }
    .badge { display:inline-block; border-radius:999px; padding:3px 9px; font-size:12px; font-weight:600; }
    .badge.available { color:var(--good); background:var(--good-weak); }
    .badge.consumed { color:var(--muted); background:var(--neutral-weak); }
    .badge.expired { color:var(--warn); background:var(--warn-weak); }
    tr.consumed td, tr.expired td { color:var(--muted); }
    tr.expired code.otp { color:var(--muted); background:transparent; border:1px dashed var(--line); letter-spacing:2px; }
    td.t-time { white-space:nowrap; font-variant-numeric:tabular-nums; }
    .empty { text-align:center; color:var(--muted); padding:36px; font-size:13px; }
  </style>
</head>
<body>
<main>
  <div class="otp-head"><h1>Swan 验证码</h1><span class="meta">每 2 秒自动刷新 · 显示最近取码记录（含已消费/已过期）</span></div>
  <div class="card"><table>
    <thead><tr><th>手机号</th><th>验证码</th><th>生成时间</th><th>过期时间</th><th>请求 ID</th><th>状态</th></tr></thead>
    <tbody id="items"><tr><td class="empty" colspan="6">加载中…</td></tr></tbody>
  </table></div>
</main>
<script>
const items = document.getElementById('items');
const BADGE_TEXT = { available: '有效', consumed: '已消费', expired: '已过期' };
function element(tag, className, text) { const node = document.createElement(tag); if (className) node.className = className; node.textContent = text || ''; return node; }
function cell(value) { return element('td', '', value); }
function toDate(value) { const date = new Date(value); return isNaN(date.getTime()) ? null : date; }
function pad(n) { return String(n).padStart(2, '0'); }
function formatTime(value) {
  const date = toDate(value);
  if (!date) return value || '';
  return date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate()) + ' ' + pad(date.getHours()) + ':' + pad(date.getMinutes()) + ':' + pad(date.getSeconds());
}
function relativeLabel(date) {
  const diff = Math.max(0, (Date.now() - date.getTime()) / 1000);
  return diff < 60 ? '刚刚' : Math.floor(diff / 60) + ' 分钟前';
}
function relativeCell(value) {
  const date = toDate(value);
  const td = element('td', 't-time', date ? relativeLabel(date) : formatTime(value));
  td.title = formatTime(value);
  if (date) td.dataset.created = String(date.getTime());
  return td;
}
function expireCell(value) {
  const date = toDate(value);
  // 记录时间是 UTC,过期时刻按本地时区显示到秒(抄码操作意义),title 保留全量
  const text = date ? pad(date.getHours()) + ':' + pad(date.getMinutes()) + ':' + pad(date.getSeconds()) : (value || '');
  const td = element('td', 't-time', text); td.title = formatTime(value); return td;
}
let lastSnapshot = '';
async function refresh() {
  try {
    const response = await fetch('/api/test/otp/recent?limit=100', { cache: 'no-store' });
    if (!response.ok) throw new Error('HTTP ' + response.status);
    const data = await response.json();
    const snapshot = JSON.stringify(data.items);
    if (snapshot === lastSnapshot) {
      for (const row of items.rows) {  // 数据未变不重绘(防打断 hover),但相对时间仍要走钟
        if (row.dataset.created) row.children[2].textContent = relativeLabel(new Date(Number(row.dataset.created)));
      }
      return;
    }
    lastSnapshot = snapshot;
    items.replaceChildren();
    if (!data.items.length) {
      const row = document.createElement('tr');
      const empty = element('td', 'empty', '暂无验证码记录，用例触发取码后约 2 秒自动出现');
      empty.colSpan = 6; row.appendChild(empty); items.appendChild(row); return;
    }
    for (const item of data.items) {
      const row = document.createElement('tr');
      row.className = item.status || '';
      const codeCell = document.createElement('td');
      codeCell.appendChild(element('code', 'otp', item.code));
      const statusCell = document.createElement('td');
      statusCell.appendChild(element('span', 'badge ' + (item.status || ''), BADGE_TEXT[item.status] || item.status || ''));
      const ridCell = document.createElement('td');
      ridCell.appendChild(element('span', 'rid', item.requestId));
      row.append(cell(item.phone), codeCell, relativeCell(item.createdAt), expireCell(item.expireAt), ridCell, statusCell);
      items.appendChild(row);
    }
  } catch (error) {
    items.replaceChildren();
    const row = document.createElement('tr');
    const empty = element('td', 'empty', '加载失败：' + error.message + '（每 2 秒自动重试）');
    empty.colSpan = 6; row.appendChild(empty); items.appendChild(row);
  }
}
refresh(); setInterval(refresh, 2000);
</script>
</body>
</html>"""


def create_server(
    host: str,
    port: int,
    database_path: str | Path,
    ingest_token: str,
    read_token: str,
    ttl_seconds: int = 300,
    allowed_phones: set[str] | None = None,
    read_auth_required: bool = False,
    ingest_auth_required: bool = False,
    captcha_source_url: str = "",
    captcha_source_timeout_seconds: float = 5,
) -> OtpGateway:
    if ingest_auth_required and not ingest_token:
        raise ValueError("OTP_INGEST_TOKEN is required when ingest auth is enabled")
    if read_auth_required and not read_token:
        raise ValueError("OTP_READ_TOKEN is required when read auth is enabled")
    if read_token and hmac.compare_digest(ingest_token, read_token):
        raise ValueError("ingest and read tokens must be different")
    if ttl_seconds <= 0:
        raise ValueError("ttl_seconds must be positive")
    return OtpGateway(
        (host, port),
        OtpStore(database_path, ttl_seconds=ttl_seconds),
        ingest_token,
        read_token,
        allowed_phones,
        read_auth_required,
        ingest_auth_required,
        CaptchaSource(captcha_source_url, captcha_source_timeout_seconds),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Receive and read OTPs for authorized automation accounts")
    parser.add_argument("--host", default=os.getenv("OTP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("OTP_PORT", "8080")))
    parser.add_argument("--db", default=os.getenv("OTP_DB", "output/otp_gateway/otp.sqlite3"))
    parser.add_argument("--ttl", type=int, default=int(os.getenv("OTP_TTL_SECONDS", "300")))
    parser.add_argument("--ingest-token", default=os.getenv("OTP_INGEST_TOKEN", ""))
    parser.add_argument("--read-token", default=os.getenv("OTP_READ_TOKEN", ""))
    parser.add_argument("--allowed-phones", default=os.getenv("OTP_ALLOWED_PHONES", ""))
    parser.add_argument("--captcha-source-url", default=os.getenv("CAPTCHA_SOURCE_URL", ""))
    parser.add_argument(
        "--captcha-source-timeout",
        type=float,
        default=float(os.getenv("CAPTCHA_SOURCE_TIMEOUT_SECONDS", "5")),
    )
    parser.add_argument(
        "--ingest-auth-required",
        type=lambda value: value.lower() in {"1", "true", "yes", "on"},
        default=os.getenv("OTP_INGEST_AUTH_REQUIRED", "false").lower() in {"1", "true", "yes", "on"},
    )
    parser.add_argument(
        "--read-auth-required",
        type=lambda value: value.lower() in {"1", "true", "yes", "on"},
        default=os.getenv("OTP_READ_AUTH_REQUIRED", "false").lower() in {"1", "true", "yes", "on"},
    )
    args = parser.parse_args()
    server = create_server(
        args.host,
        args.port,
        args.db,
        args.ingest_token,
        args.read_token,
        ttl_seconds=args.ttl,
        allowed_phones={phone.strip() for phone in args.allowed_phones.split(",") if phone.strip()}
        or None,
        read_auth_required=args.read_auth_required,
        ingest_auth_required=args.ingest_auth_required,
        captcha_source_url=args.captcha_source_url,
        captcha_source_timeout_seconds=args.captcha_source_timeout,
    )
    print(f"OTP gateway listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
