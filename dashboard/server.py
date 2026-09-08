from __future__ import annotations

import argparse
import json
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
                """
            )

    def create_run(self, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = str(payload.get("run_id") or "").strip()
        platform = str(payload.get("platform") or "").strip().lower()
        if not run_id:
            raise ValueError("run_id is required")
        if platform not in {"android", "ios"}:
            raise ValueError("platform must be android or ios")
        started_at = str(payload.get("started_at") or utc_now())
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO runs (
                    run_id, platform, status, app_version, device, jenkins_build,
                    started_at, metadata_json
                ) VALUES (?, ?, 'running', ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    platform=excluded.platform,
                    app_version=excluded.app_version,
                    device=excluded.device,
                    jenkins_build=excluded.jenkins_build,
                    metadata_json=excluded.metadata_json
                """,
                (
                    run_id,
                    platform,
                    str(payload.get("app_version") or ""),
                    str(payload.get("device") or ""),
                    str(payload.get("jenkins_build") or ""),
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

    def list_runs(self, platform: str = "", limit: int = 50) -> list[dict[str, Any]]:
        limit = min(max(int(limit), 1), 200)
        query = "SELECT * FROM runs"
        parameters: list[Any] = []
        if platform in {"android", "ios"}:
            query += " WHERE platform=?"
            parameters.append(platform)
        query += " ORDER BY started_at DESC LIMIT ?"
        parameters.append(limit)
        with self.transaction() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self.serialize_run(row) for row in rows]


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
            limit = query.get("limit", ["50"])[0]
            try:
                runs = self.store.list_runs(platform=platform, limit=int(limit))
            except (TypeError, ValueError):
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": runs})
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


DASHBOARD_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>UIAutotest 测试历史</title>
  <style>
    :root { color-scheme: light; --ink:#172033; --muted:#667085; --line:#e6e9ef; --bg:#f5f7fb; --card:#fff; --brand:#405cf5; --good:#087f5b; --bad:#c92a2a; --warn:#ad6800; }
    * { box-sizing:border-box; } body { margin:0; color:var(--ink); background:var(--bg); font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }
    header { background:linear-gradient(120deg,#172554,#405cf5); color:#fff; padding:28px max(24px,calc((100% - 1240px)/2)); }
    header h1 { margin:0 0 5px; font-size:25px; } header p { margin:0; opacity:.78; }
    main { max-width:1240px; margin:24px auto; padding:0 20px 48px; } .toolbar { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:18px; }
    select,button { border:1px solid var(--line); border-radius:8px; background:#fff; padding:9px 12px; color:var(--ink); cursor:pointer; } button.primary { background:var(--brand); color:#fff; border-color:var(--brand); }
    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:18px; } .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:18px; box-shadow:0 2px 10px rgba(23,32,51,.03); }
    .stat-label { color:var(--muted); font-size:12px; } .stat-value { font-size:25px; font-weight:700; margin-top:4px; } .table-card { padding:0; overflow:hidden; }
    table { border-collapse:collapse; width:100%; } th,td { padding:13px 15px; border-bottom:1px solid var(--line); text-align:left; white-space:nowrap; } th { color:var(--muted); background:#fafbfc; font-size:12px; font-weight:600; } tbody tr { cursor:pointer; } tbody tr:hover { background:#f8f9ff; }
    .badge { border-radius:999px; padding:3px 9px; font-size:12px; font-weight:600; display:inline-block; } .passed { color:var(--good); background:#e6fcf5; } .failed,.error { color:var(--bad); background:#fff5f5; } .running { color:var(--brand); background:#edf2ff; } .skipped { color:var(--warn); background:#fff9db; }
    .empty { padding:44px; text-align:center; color:var(--muted); } .detail { margin-top:18px; display:none; } .detail h2 { margin:0 0 14px; font-size:18px; } .detail-head { display:flex; justify-content:space-between; gap:12px; align-items:start; } .meta { color:var(--muted); font-size:13px; }
    .case { border:1px solid var(--line); border-radius:10px; margin:10px 0; padding:13px 15px; background:#fff; } .case summary { cursor:pointer; list-style:none; } .case summary::-webkit-details-marker { display:none; } .case summary::before { content:"▸"; margin-right:8px; color:var(--muted); } .case[open] summary::before { content:"▾"; }
    pre { white-space:pre-wrap; word-break:break-word; background:#f7f8fa; border-radius:8px; padding:12px; max-height:300px; overflow:auto; } .case-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin:12px 0; color:var(--muted); font-size:12px; }
    @media (max-width:800px) { .stats { grid-template-columns:repeat(2,1fr); } .toolbar,.detail-head { align-items:stretch; flex-direction:column; } .table-card { overflow-x:auto; } .case-grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header><h1>UIAutotest 测试历史</h1><p>Android / iOS 自动化执行结果、用例日志与视觉断言证据</p></header>
  <main>
    <div class="toolbar"><div><label for="platform">平台：</label><select id="platform"><option value="">全部</option><option value="android">Android</option><option value="ios">iOS</option></select></div><button class="primary" id="refresh">刷新</button></div>
    <section class="stats"><div class="card"><div class="stat-label">执行次数</div><div class="stat-value" id="run-count">-</div></div><div class="card"><div class="stat-label">平均通过率</div><div class="stat-value" id="pass-rate">-</div></div><div class="card"><div class="stat-label">最近一次状态</div><div class="stat-value" id="latest-status">-</div></div><div class="card"><div class="stat-label">最近一次耗时</div><div class="stat-value" id="latest-duration">-</div></div></section>
    <section class="card table-card"><table><thead><tr><th>执行 ID</th><th>平台</th><th>状态</th><th>通过率</th><th>用例数</th><th>耗时</th><th>开始时间</th></tr></thead><tbody id="runs"><tr><td colspan="7" class="empty">加载中…</td></tr></tbody></table></section>
    <section class="card detail" id="detail"><div class="detail-head"><div><h2 id="detail-title"></h2><div class="meta" id="detail-meta"></div></div><button id="close-detail">关闭</button></div><div id="cases"></div></section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    const statusText = {running:'执行中', passed:'通过', failed:'失败', skipped:'跳过', error:'错误'};
    const safe = (value) => String(value ?? '').replace(/[&<>\"']/g, (character) => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[character]));
    const formatDate = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-';
    const formatDuration = (seconds) => { seconds = Number(seconds || 0); if (seconds < 60) return `${seconds.toFixed(1)} 秒`; return `${Math.floor(seconds / 60)} 分 ${Math.round(seconds % 60)} 秒`; };
    const badge = (status) => `<span class="badge ${status}">${statusText[status] || status}</span>`;
    async function loadRuns() {
      const platform = $('platform').value; const query = platform ? `?platform=${platform}` : '';
      const response = await fetch(`/api/runs${query}`); const data = await response.json(); const runs = data.items || [];
      $('run-count').textContent = runs.length;
      const completed = runs.filter((run) => run.total_cases);
      const average = completed.length ? completed.reduce((sum, run) => sum + run.pass_rate, 0) / completed.length : 0;
      $('pass-rate').textContent = `${average.toFixed(1)}%`;
      $('latest-status').innerHTML = runs.length ? badge(runs[0].status) : '-';
      $('latest-duration').textContent = runs.length ? formatDuration(runs[0].duration_seconds) : '-';
      const tbody = $('runs'); tbody.innerHTML = '';
      if (!runs.length) { tbody.innerHTML = '<tr><td colspan="7" class="empty">暂无执行记录</td></tr>'; return; }
      runs.forEach((run) => { const row = document.createElement('tr'); row.innerHTML = `<td>${safe(run.run_id)}</td><td>${safe(run.platform.toUpperCase())}</td><td>${badge(run.status)}</td><td>${run.pass_rate.toFixed(1)}%</td><td>${run.total_cases}</td><td>${formatDuration(run.duration_seconds)}</td><td>${safe(formatDate(run.started_at))}</td>`; row.onclick = () => showRun(run.run_id); tbody.appendChild(row); });
    }
    async function showRun(runId) {
      const response = await fetch(`/api/runs/${encodeURIComponent(runId)}`); const run = await response.json(); $('detail').style.display = 'block'; $('detail-title').textContent = `${run.run_id} · ${run.platform.toUpperCase()} ${statusText[run.status] || run.status}`; $('detail-meta').textContent = `开始：${formatDate(run.started_at)}　结束：${formatDate(run.ended_at)}　耗时：${formatDuration(run.duration_seconds)}　通过率：${run.pass_rate.toFixed(1)}%`;
      const cases = $('cases'); cases.innerHTML = ''; (run.cases || []).forEach((item) => { const box = document.createElement('details'); box.className = 'case'; const artifacts = JSON.stringify(item.artifacts || {}, null, 2); box.innerHTML = `<summary>${badge(item.status)}　${safe(item.name)} <span class="meta">${formatDuration(item.duration_seconds)}</span></summary><div class="case-grid"><span>开始：${safe(formatDate(item.started_at))}</span><span>结束：${safe(formatDate(item.ended_at))}</span><span>用例 ID：${safe(item.case_id)}</span></div>${item.error ? `<strong>错误</strong><pre>${safe(item.error)}</pre>` : ''}<strong>执行日志</strong><pre>${safe(item.log || '无日志')}</pre><strong>附件</strong><pre>${safe(artifacts)}</pre>`; cases.appendChild(box); });
      $('detail').scrollIntoView({behavior:'smooth'});
    }
    $('refresh').onclick = loadRuns; $('platform').onchange = loadRuns; $('close-detail').onclick = () => $('detail').style.display = 'none'; loadRuns().catch((error) => { $('runs').innerHTML = `<tr><td colspan="7" class="empty">加载失败：${error}</td></tr>`; });
  </script>
</body>
</html>"""


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
