from __future__ import annotations

import argparse
import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "output" / "dashboard.sqlite3"

# 平台取值集合：flutter = Flutter App(跑在 Android 设备上)，pc = 桌面端
VALID_PLATFORMS = {"android", "ios", "flutter", "pc"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_status(value: Any) -> str:
    status = str(value or "error").strip().lower()
    aliases = {
        "pass": "passed",
        "passed": "passed",
        "success": "passed",
        "fail": "failed",
        "failed": "failed",
        "skip": "skipped",
        "skipped": "skipped",
        "error": "error",
        "broken": "error",
    }
    return aliases.get(status, "error")


def json_object(value: Any) -> str:
    if value is None:
        return "{}"
    if isinstance(value, str):
        try:
            json.loads(value)
            return value
        except json.JSONDecodeError:
            return json.dumps({"value": value}, ensure_ascii=False)
    return json.dumps(value, ensure_ascii=False)


class DashboardStore:
    def __init__(self, database_path: str | Path = DEFAULT_DATABASE):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def transaction(self):
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'running',
                    app_version TEXT NOT NULL DEFAULT '',
                    device TEXT NOT NULL DEFAULT '',
                    jenkins_build TEXT NOT NULL DEFAULT '',
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds REAL NOT NULL DEFAULT 0,
                    total_cases INTEGER NOT NULL DEFAULT 0,
                    passed_cases INTEGER NOT NULL DEFAULT 0,
                    failed_cases INTEGER NOT NULL DEFAULT 0,
                    skipped_cases INTEGER NOT NULL DEFAULT 0,
                    error_cases INTEGER NOT NULL DEFAULT 0,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS cases (
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    duration_seconds REAL NOT NULL DEFAULT 0,
                    log TEXT NOT NULL DEFAULT '',
                    error TEXT NOT NULL DEFAULT '',
                    artifacts_json TEXT NOT NULL DEFAULT '{}',
                    PRIMARY KEY (run_id, case_id),
                    FOREIGN KEY (run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_runs_started_at ON runs(started_at DESC);
                CREATE INDEX IF NOT EXISTS idx_cases_run_id ON cases(run_id);
                CREATE INDEX IF NOT EXISTS idx_cases_case_id ON cases(case_id);
                """
            )
            # 轻量迁移：老库补列（runs.apk_id）
            run_columns = {row["name"] for row in connection.execute("PRAGMA table_info(runs)")}
            if "apk_id" not in run_columns:
                connection.execute("ALTER TABLE runs ADD COLUMN apk_id TEXT NOT NULL DEFAULT ''")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS apks (
                    apk_id TEXT PRIMARY KEY,
                    app_version TEXT NOT NULL DEFAULT '',
                    branch TEXT NOT NULL DEFAULT '',
                    commit_hash TEXT NOT NULL DEFAULT '',
                    flavor TEXT NOT NULL DEFAULT '',
                    source TEXT NOT NULL DEFAULT 'manual',
                    file_path TEXT NOT NULL DEFAULT '',
                    file_hash TEXT NOT NULL DEFAULT '',
                    notes TEXT NOT NULL DEFAULT '',
                    registered_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_apks_registered_at ON apks(registered_at DESC);
                """
            )

    def create_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = str(payload.get("run_id") or "").strip()
        platform = str(payload.get("platform") or "").strip().lower()
        if not run_id:
            raise ValueError("run_id is required")
        if platform not in VALID_PLATFORMS:
            raise ValueError(f"platform must be one of {sorted(VALID_PLATFORMS)}")
        started_at = str(payload.get("started_at") or utc_now())
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO runs (
                    run_id, platform, status, app_version, device, jenkins_build,
                    apk_id, started_at, metadata_json
                ) VALUES (?, ?, 'running', ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    platform=excluded.platform,
                    app_version=excluded.app_version,
                    device=excluded.device,
                    jenkins_build=excluded.jenkins_build,
                    apk_id=excluded.apk_id,
                    metadata_json=excluded.metadata_json
                """,
                (
                    run_id,
                    platform,
                    str(payload.get("app_version") or ""),
                    str(payload.get("device") or ""),
                    str(payload.get("jenkins_build") or ""),
                    str(payload.get("apk_id") or ""),
                    started_at,
                    json_object(payload.get("metadata")),
                ),
            )
        return self.get_run(run_id)

    def upsert_case(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        case_id = str(payload.get("case_id") or "").strip()
        if not case_id:
            raise ValueError("case_id is required")
        status = normalize_status(payload.get("status"))
        started_at = str(payload.get("started_at") or utc_now())
        with self.transaction() as connection:
            run = connection.execute(
                "SELECT platform FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if run is None:
                raise KeyError(f"run not found: {run_id}")
            connection.execute(
                """
                INSERT INTO cases (
                    run_id, case_id, name, platform, status, started_at, ended_at,
                    duration_seconds, log, error, artifacts_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, case_id) DO UPDATE SET
                    name=excluded.name,
                    platform=excluded.platform,
                    status=excluded.status,
                    started_at=excluded.started_at,
                    ended_at=excluded.ended_at,
                    duration_seconds=excluded.duration_seconds,
                    log=excluded.log,
                    error=excluded.error,
                    artifacts_json=excluded.artifacts_json
                """,
                (
                    run_id,
                    case_id,
                    str(payload.get("name") or case_id),
                    str(payload.get("platform") or run["platform"]),
                    status,
                    started_at,
                    payload.get("ended_at"),
                    float(payload.get("duration_seconds") or 0),
                    str(payload.get("log") or ""),
                    str(payload.get("error") or ""),
                    json_object(payload.get("artifacts")),
                ),
            )
        return self.get_case(run_id, case_id)

    def complete_run(self, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        ended_at = str(payload.get("ended_at") or utc_now())
        with self.transaction() as connection:
            run = connection.execute(
                "SELECT started_at FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
            if run is None:
                raise KeyError(f"run not found: {run_id}")
            rows = connection.execute(
                "SELECT status, COUNT(*) AS count FROM cases WHERE run_id = ? GROUP BY status",
                (run_id,),
            ).fetchall()
            counts = {row["status"]: int(row["count"]) for row in rows}
            total = sum(counts.values())
            passed = counts.get("passed", 0)
            failed = counts.get("failed", 0)
            skipped = counts.get("skipped", 0)
            errors = counts.get("error", 0)
            status = normalize_status(payload.get("status"))
            if status == "passed" and (failed or errors):
                status = "failed"
            if status not in {"passed", "failed", "skipped", "error"}:
                status = "failed" if failed or errors else "passed"
            duration = float(payload.get("duration_seconds") or 0)
            if duration <= 0:
                duration = self.duration_between(run["started_at"], ended_at)
            connection.execute(
                """
                UPDATE runs SET status=?, ended_at=?, duration_seconds=?, total_cases=?,
                    passed_cases=?, failed_cases=?, skipped_cases=?, error_cases=?
                WHERE run_id=?
                """,
                (status, ended_at, duration, total, passed, failed, skipped, errors, run_id),
            )
        return self.get_run(run_id)

    @staticmethod
    def duration_between(started_at: str, ended_at: str) -> float:
        try:
            start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
            return max(0.0, (end - start).total_seconds())
        except ValueError:
            return 0.0

    @staticmethod
    def serialize_run(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
        item["pass_rate"] = round(
            item["passed_cases"] / item["total_cases"] * 100, 1
        ) if item["total_cases"] else 0.0
        return item

    @staticmethod
    def serialize_case(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["artifacts"] = json.loads(item.pop("artifacts_json") or "{}")
        return item

    def get_case(self, run_id: str, case_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM cases WHERE run_id=? AND case_id=?", (run_id, case_id)
            ).fetchone()
        if row is None:
            raise KeyError(f"case not found: {run_id}/{case_id}")
        return self.serialize_case(row)

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None:
                raise KeyError(f"run not found: {run_id}")
            cases = connection.execute(
                "SELECT * FROM cases WHERE run_id=? ORDER BY started_at, case_id", (run_id,)
            ).fetchall()
        result = self.serialize_run(row)
        result["cases"] = [self.serialize_case(case) for case in cases]
        return result

    def list_runs(self, platform: str = "", limit: int = 50, apk_id: str = "") -> list[dict[str, Any]]:
        limit = min(max(int(limit), 1), 200)
        query = "SELECT * FROM runs"
        conditions: list[str] = []
        parameters: list[Any] = []
        if platform in VALID_PLATFORMS:
            conditions.append("platform=?")
            parameters.append(platform)
        if apk_id:
            conditions.append("apk_id=?")
            parameters.append(apk_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY started_at DESC LIMIT ?"
        parameters.append(limit)
        with self.transaction() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self.serialize_run(row) for row in rows]

    # ==================== 安装包管理 ====================

    def register_apk(self, payload: dict[str, Any]) -> dict[str, Any]:
        apk_id = str(payload.get("apk_id") or "").strip()
        if not apk_id:
            raise ValueError("apk_id is required")
        registered_at = str(payload.get("registered_at") or utc_now())
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO apks (
                    apk_id, app_version, branch, commit_hash, flavor, source,
                    file_path, file_hash, notes, registered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(apk_id) DO UPDATE SET
                    app_version=excluded.app_version,
                    branch=excluded.branch,
                    commit_hash=excluded.commit_hash,
                    flavor=excluded.flavor,
                    source=excluded.source,
                    file_path=excluded.file_path,
                    file_hash=excluded.file_hash,
                    notes=excluded.notes
                """,
                (
                    apk_id,
                    str(payload.get("app_version") or ""),
                    str(payload.get("branch") or ""),
                    str(payload.get("commit_hash") or ""),
                    str(payload.get("flavor") or ""),
                    str(payload.get("source") or "manual"),
                    str(payload.get("file_path") or ""),
                    str(payload.get("file_hash") or ""),
                    str(payload.get("notes") or ""),
                    registered_at,
                ),
            )
        return self.get_apk(apk_id)

    def get_apk(self, apk_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute("SELECT * FROM apks WHERE apk_id=?", (apk_id,)).fetchone()
        if row is None:
            raise KeyError(f"apk not found: {apk_id}")
        return dict(row)

    def list_apks(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = min(max(int(limit), 1), 200)
        with self.transaction() as connection:
            rows = connection.execute(
                "SELECT * FROM apks ORDER BY registered_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    # ==================== 用例执行历史（三视角之"某用例"） ====================

    def get_case_history(self, case_id: str, limit: int = 20) -> list[dict[str, Any]]:
        limit = min(max(int(limit), 1), 100)
        with self.transaction() as connection:
            rows = connection.execute(
                """
                SELECT c.case_id, c.name, c.status, c.started_at, c.ended_at,
                       c.duration_seconds, c.error,
                       r.run_id, r.platform, r.status AS run_status,
                       r.apk_id, r.app_version, r.device, r.started_at AS run_started_at
                FROM cases c JOIN runs r ON c.run_id = r.run_id
                WHERE c.case_id = ?
                ORDER BY c.started_at DESC LIMIT ?
                """,
                (case_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def search_case_ids(self, keyword: str, limit: int = 20) -> list[dict[str, Any]]:
        """按关键词模糊搜用例(取最近出现的 case_id),供历史页选择。"""
        limit = min(max(int(limit), 1), 100)
        pattern = f"%{keyword}%"
        with self.transaction() as connection:
            rows = connection.execute(
                """
                SELECT c.case_id, MAX(c.name) AS name, COUNT(*) AS executions,
                       MAX(c.started_at) AS last_seen
                FROM cases c WHERE c.case_id LIKE ?
                GROUP BY c.case_id ORDER BY last_seen DESC LIMIT ?
                """,
                (pattern, limit),
            ).fetchall()
        return [dict(row) for row in rows]


class DashboardHandler(BaseHTTPRequestHandler):
    store: DashboardStore

    def log_message(self, format_string: str, *args: Any) -> None:
        return

    def send_json(self, payload: Any, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message: str, status: int) -> None:
        self.send_json({"error": message}, status)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Dashboard-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = DASHBOARD_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/health":
            self.send_json({"status": "ok"})
            return
        if parsed.path == "/api/runs":
            query = parse_qs(parsed.query)
            platform = query.get("platform", [""])[0].lower()
            apk_id = query.get("apk_id", [""])[0]
            limit = query.get("limit", ["50"])[0]
            try:
                runs = self.store.list_runs(platform=platform, limit=int(limit), apk_id=apk_id)
            except (TypeError, ValueError):
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": runs})
            return
        if parsed.path == "/api/apks":
            query = parse_qs(parsed.query)
            try:
                limit = int(query.get("limit", ["50"])[0])
            except ValueError:
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": self.store.list_apks(limit=limit)})
            return
        if parsed.path.startswith("/api/cases/") and parsed.path.endswith("/history"):
            case_id = parsed.path.removeprefix("/api/cases/").removesuffix("/history").strip("/")
            if not case_id:
                self.send_error_json("case_id is required", HTTPStatus.BAD_REQUEST)
                return
            query = parse_qs(parsed.query)
            try:
                limit = int(query.get("limit", ["20"])[0])
            except ValueError:
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": self.store.get_case_history(case_id, limit=limit)})
            return
        if parsed.path == "/api/cases/search":
            query = parse_qs(parsed.query)
            keyword = query.get("q", [""])[0].strip()
            if not keyword:
                self.send_error_json("q is required", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": self.store.search_case_ids(keyword)})
            return
        if parsed.path == "/api/gateway/health":
            # 验证码工具页的健康卡片:平台侧代理 otp-gateway /healthz,避免浏览器跨域
            import urllib.request as _urlreq
            gateway = os.environ.get("OTP_GATEWAY_URL", "http://192.168.12.166:18080").rstrip("/")
            try:
                with _urlreq.urlopen(f"{gateway}/healthz", timeout=5) as response:
                    body = response.read().decode("utf-8", "replace")
                self.send_json({"ok": True, "gateway": gateway, "detail": body[:200]})
            except Exception as error:  # noqa: BLE001 — 健康代理失败本身就是信息
                self.send_json({"ok": False, "gateway": gateway, "detail": str(error)})
            return
        if parsed.path.startswith("/api/runs/"):
            run_id = parsed.path.removeprefix("/api/runs/").strip("/")
            if not run_id:
                self.send_error_json("run_id is required", HTTPStatus.BAD_REQUEST)
                return
            try:
                self.send_json(self.store.get_run(run_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
            return
        self.send_error_json("not found", HTTPStatus.NOT_FOUND)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 5 * 1024 * 1024:
            raise ValueError("request body is too large")
        body = self.rfile.read(length)
        value = json.loads(body.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def do_POST(self) -> None:
        try:
            payload = self.read_json()
            parsed = urlparse(self.path)
            if parsed.path == "/api/runs":
                self.send_json(self.store.create_run(payload), HTTPStatus.CREATED)
                return
            if parsed.path == "/api/apks":
                self.send_json(self.store.register_apk(payload), HTTPStatus.CREATED)
                return
            if parsed.path.startswith("/api/runs/") and parsed.path.endswith("/cases"):
                run_id = parsed.path.removeprefix("/api/runs/").removesuffix("/cases").strip("/")
                self.send_json(self.store.upsert_case(run_id, payload), HTTPStatus.CREATED)
                return
            if parsed.path.startswith("/api/runs/") and parsed.path.endswith("/complete"):
                run_id = parsed.path.removeprefix("/api/runs/").removesuffix("/complete").strip("/")
                self.send_json(self.store.complete_run(run_id, payload))
                return
            self.send_error_json("not found", HTTPStatus.NOT_FOUND)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_error_json(str(error), HTTPStatus.BAD_REQUEST)
        except KeyError as error:
            self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
        except Exception as error:
            self.send_error_json(str(error), HTTPStatus.INTERNAL_SERVER_ERROR)


def create_server(host: str = "127.0.0.1", port: int = 8080, database_path: str | Path = DEFAULT_DATABASE) -> ThreadingHTTPServer:
    store = DashboardStore(database_path)

    class BoundDashboardHandler(DashboardHandler):
        pass

    BoundDashboardHandler.store = store
    return ThreadingHTTPServer((host, port), BoundDashboardHandler)


# 页面独立维护在 dashboard/page.html(四页签:会话/包管理/用例历史/验证码工具)
DASHBOARD_HTML = (Path(__file__).resolve().parent / "page.html").read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="UIAutotest test history dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--database", default=str(DEFAULT_DATABASE))
    args = parser.parse_args()
    server = create_server(args.host, args.port, args.database)
    print(f"Dashboard listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
