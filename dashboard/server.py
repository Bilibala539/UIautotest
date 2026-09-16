from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import date, datetime, time as dt_time, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "output" / "dashboard.sqlite3"


def _load_dotenv_local() -> None:
    """加载项目根 .env.local(部署机专属配置:禅道凭据等,不进 git)。

    已存在的环境变量优先,文件值只作补充。
    """
    env_file = PROJECT_ROOT / ".env.local"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv_local()

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


def _stale_cutoff() -> str:
    """busy 设备的自愈阈值:4 小时前(ISO 时间字符串可直接比较)。"""
    from datetime import timedelta
    return (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(timespec="seconds")


# ==================== 流水线配置:频率解析与下次执行时间(纯函数,便于单测) ====================

PIPELINE_SCHEDULE_TYPES = ("once", "daily", "interval", "weekly")
_HHMM_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def parse_hhmm(value: Any) -> tuple[int, int]:
    """校验 'HH:MM'(24 小时制)并拆成 (hour, minute);非法抛 ValueError。"""
    text = str(value or "").strip()
    match = _HHMM_RE.match(text)
    if not match:
        raise ValueError(f"time 必须是合法的 HH:MM(24 小时制),收到: {value!r}")
    return int(match.group(1)), int(match.group(2))


def parse_run_at(value: Any) -> datetime:
    """解析 once.run_at,接受 'YYYY-MM-DD HH:MM' 或 ISO 格式;返回本地 naive 分钟精度。"""
    text = str(value or "").strip()
    if not text:
        raise ValueError("once.run_at 必填,格式 YYYY-MM-DD HH:MM")
    try:
        moment = datetime.fromisoformat(text.replace("T", " "))
    except ValueError:
        raise ValueError(f"run_at 时间格式非法(应为 YYYY-MM-DD HH:MM): {value!r}") from None
    if moment.tzinfo is not None:
        moment = moment.astimezone().replace(tzinfo=None)
    return moment.replace(second=0, microsecond=0)


def validate_schedule_param(schedule_type: str, param: dict[str, Any]) -> None:
    """校验各频率的参数结构,非法抛 ValueError(建/改配置时把关)。"""
    if schedule_type == "once":
        parse_run_at(param.get("run_at"))
    elif schedule_type == "daily":
        parse_hhmm(param.get("time"))
    elif schedule_type == "interval":
        try:
            every_days = int(param.get("every_days"))
        except (TypeError, ValueError):
            raise ValueError("interval.every_days 必须是正整数") from None
        if every_days < 1:
            raise ValueError("interval.every_days 必须 >= 1")
        parse_hhmm(param.get("time"))
    elif schedule_type == "weekly":
        weekdays = param.get("weekdays")
        if not isinstance(weekdays, list) or not weekdays:
            raise ValueError("weekly.weekdays 必须是非空数组(0=周日 … 6=周六)")
        try:
            normalized = {int(w) for w in weekdays}
        except (TypeError, ValueError):
            raise ValueError("weekly.weekdays 必须是 0-6 的整数数组") from None
        if not normalized.issubset(set(range(7))):
            raise ValueError("weekly.weekdays 取值必须落在 0-6(0=周日)")
        parse_hhmm(param.get("time"))


def validate_pipeline_config(payload: dict[str, Any]) -> dict[str, Any]:
    """校验并规范化流水线配置字段;schedule_param 统一落成紧凑 JSON 字符串。"""
    config_id = str(payload.get("config_id") or "").strip()
    name = str(payload.get("name") or "").strip()
    if not config_id:
        raise ValueError("config_id 必填")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", config_id):
        raise ValueError("config_id 只能包含字母/数字/._- 且长度 1-64")
    if not name:
        raise ValueError("name 必填")
    schedule_type = str(payload.get("schedule_type") or "").strip().lower()
    if schedule_type not in PIPELINE_SCHEDULE_TYPES:
        raise ValueError(f"schedule_type 必须是 {'/'.join(PIPELINE_SCHEDULE_TYPES)}")
    raw_param = payload.get("schedule_param")
    if isinstance(raw_param, str):
        try:
            param = json.loads(raw_param or "{}")
        except json.JSONDecodeError:
            raise ValueError("schedule_param 不是合法 JSON") from None
    else:
        param = raw_param or {}
    if not isinstance(param, dict):
        raise ValueError("schedule_param 必须是 JSON 对象")
    validate_schedule_param(schedule_type, param)
    return {
        "config_id": config_id,
        "name": name,
        "description": str(payload.get("description") or "").strip(),
        "suite_id": str(payload.get("suite_id") or "").strip(),
        "include_build": 1 if payload.get("include_build") in (1, True, "1", "true", "on") else 0,
        "schedule_type": schedule_type,
        "schedule_param": json.dumps(param, ensure_ascii=False),
        "enabled": 0 if payload.get("enabled") in (0, False, "0", "false", "off") else 1,
    }


def compute_next_run_at(
    schedule_type: str,
    schedule_param: str | dict,
    now: datetime | None = None,
    interval_anchor: str = "1970-01-01",
) -> str:
    """计算下次执行时间(本地 naive ISO 字符串,分钟精度);无法计算返回 ''。

    语义:返回 >= now(截断到分钟)的最近一次命中时刻。因此调度器按
    next_run_at <= now 触发时,天然只在"命中那一分钟"内生效,不会补跑陈旧欠账。
    interval 以 interval_anchor(默认 1970-01-01)为相位锚点,保证同参数计算确定。
    weekly.weekdays 用前端约定 0=周日 … 6=周六,内部换算成 Python weekday()。
    """
    if isinstance(schedule_param, str):
        try:
            param = json.loads(schedule_param or "{}")
        except json.JSONDecodeError:
            return ""
    else:
        param = schedule_param or {}
    if not isinstance(param, dict):
        return ""
    base = (now or datetime.now()).replace(second=0, microsecond=0)
    if base.tzinfo is not None:
        base = base.astimezone().replace(tzinfo=None)
    try:
        if schedule_type == "once":
            target = parse_run_at(param.get("run_at"))
            return target.isoformat(timespec="seconds") if target >= base else ""
        if schedule_type == "daily":
            hour, minute = parse_hhmm(param.get("time"))
            candidate = base.replace(hour=hour, minute=minute)
            if candidate < base:
                candidate += timedelta(days=1)  # 当天时刻已过 → 明天同一时刻(跨天)
            return candidate.isoformat(timespec="seconds")
        if schedule_type == "interval":
            every_days = int(param.get("every_days"))
            if every_days < 1:
                return ""
            hour, minute = parse_hhmm(param.get("time"))
            anchor_date = date.fromisoformat(str(interval_anchor)[:10])
            for offset in range(every_days + 1):
                day = base.date() + timedelta(days=offset)
                if (day - anchor_date).days % every_days == 0:
                    candidate = datetime.combine(day, dt_time(hour, minute))
                    if candidate >= base:
                        return candidate.isoformat(timespec="seconds")
            return ""
        if schedule_type == "weekly":
            hour, minute = parse_hhmm(param.get("time"))
            weekdays = {((int(w) - 1) % 7) for w in param.get("weekdays") or []}
            for offset in range(8):  # 7 天内必命中,留 1 天余量(跨周边界)
                day = base.date() + timedelta(days=offset)
                if day.weekday() in weekdays:
                    candidate = datetime.combine(day, dt_time(hour, minute))
                    if candidate >= base:
                        return candidate.isoformat(timespec="seconds")
            return ""
    except (ValueError, TypeError):
        return ""
    return ""


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
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL DEFAULT '',
                    platform TEXT NOT NULL DEFAULT 'flutter',
                    model TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'online_idle',
                    current_run TEXT NOT NULL DEFAULT '',
                    busy_since TEXT,
                    last_assigned_at TEXT,
                    last_heartbeat TEXT,
                    registered_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
                CREATE TABLE IF NOT EXISTS pipeline_jobs (
                    job_id TEXT PRIMARY KEY,
                    trigger_source TEXT NOT NULL DEFAULT 'manual',
                    branch TEXT NOT NULL DEFAULT '',
                    platform TEXT NOT NULL DEFAULT 'flutter',
                    case_filter TEXT NOT NULL DEFAULT '',
                    apk_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    claimed_by TEXT NOT NULL DEFAULT '',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    claimed_at TEXT,
                    finished_at TEXT,
                    result_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_status ON pipeline_jobs(status);
                CREATE TABLE IF NOT EXISTS case_defs (
                    case_id TEXT PRIMARY KEY,
                    case_type TEXT NOT NULL DEFAULT 'auto',
                    title TEXT NOT NULL DEFAULT '',
                    module TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL DEFAULT '',
                    source TEXT NOT NULL DEFAULT '',
                    source_bug TEXT NOT NULL DEFAULT '',
                    file_path TEXT NOT NULL DEFAULT '',
                    content TEXT NOT NULL DEFAULT '',
                    linked_case_id TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_case_defs_module ON case_defs(module);
                """
            )
            # 流水线定时配置(调度器每 30s 轮询,到点 POST {id}/run 建 schedule 任务)
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS pipeline_configs (
                    config_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    suite_id TEXT NOT NULL DEFAULT '',
                    include_build INTEGER NOT NULL DEFAULT 0,
                    schedule_type TEXT NOT NULL,
                    schedule_param TEXT NOT NULL DEFAULT '',
                    enabled INTEGER NOT NULL DEFAULT 1,
                    last_run_at TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
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

    # ==================== 设备池 ====================

    def register_device(self, payload: dict[str, Any]) -> dict[str, Any]:
        device_id = str(payload.get("device_id") or "").strip()
        if not device_id:
            raise ValueError("device_id is required")
        now = utc_now()
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT status FROM devices WHERE device_id=?", (device_id,)
            ).fetchone()
            # 心跳/注册刷新在线时间;busy/disabled 的设备注册(执行机自报)不覆盖其状态
            if row is None:
                connection.execute(
                    """
                    INSERT INTO devices (
                        device_id, name, platform, model, status, last_heartbeat,
                        registered_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        device_id,
                        str(payload.get("name") or ""),
                        str(payload.get("platform") or "flutter"),
                        str(payload.get("model") or ""),
                        str(payload.get("status") or "online_idle"),
                        now, now,
                        json_object(payload.get("metadata")),
                    ),
                )
            else:
                keep_status = row["status"] if row["status"] in {"busy", "disabled"} else "online_idle"
                connection.execute(
                    """
                    UPDATE devices SET name=?, platform=?, model=?, status=?,
                        last_heartbeat=?, metadata_json=?
                    WHERE device_id=?
                    """,
                    (
                        str(payload.get("name") or ""),
                        str(payload.get("platform") or "flutter"),
                        str(payload.get("model") or ""),
                        keep_status,
                        now,
                        json_object(payload.get("metadata")),
                        device_id,
                    ),
                )
        return self.get_device(device_id)

    def get_device(self, device_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute("SELECT * FROM devices WHERE device_id=?", (device_id,)).fetchone()
        if row is None:
            raise KeyError(f"device not found: {device_id}")
        return self._serialize_device(row)

    @staticmethod
    def _serialize_device(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
        return item

    def list_devices(self) -> list[dict[str, Any]]:
        with self.transaction() as connection:
            rows = connection.execute("SELECT * FROM devices ORDER BY device_id").fetchall()
        return [self._serialize_device(row) for row in rows]

    def acquire_device(self, payload: dict[str, Any]) -> dict[str, Any]:
        """领取一台空闲设备:平台匹配 + 最久未用优先(平均分配)。"""
        run_id = str(payload.get("run_id") or "").strip()
        if not run_id:
            raise ValueError("run_id is required")
        platform = str(payload.get("platform") or "flutter").strip().lower()
        prefer = [str(s) for s in (payload.get("prefer") or [])]
        now = utc_now()
        with self.transaction() as connection:
            rows = connection.execute(
                "SELECT * FROM devices WHERE status='online_idle' AND platform=?",
                (platform,),
            ).fetchall()
            if not rows:
                # 自愈:busy 超 4 小时且心跳停滞的设备视为 stale(执行机崩溃/拔线),回收重用
                connection.execute(
                    """
                    UPDATE devices SET status='online_idle', current_run='', busy_since=NULL
                    WHERE status='busy' AND platform=? AND busy_since < ?
                    """,
                    (platform, _stale_cutoff()),
                )
                rows = connection.execute(
                    "SELECT * FROM devices WHERE status='online_idle' AND platform=?",
                    (platform,),
                ).fetchall()
            if not rows:
                raise LookupError(f"no idle device for platform={platform}")

            def _rank(row: sqlite3.Row) -> tuple:
                return (0 if row["device_id"] in prefer else 1,
                        row["last_assigned_at"] or "")

            chosen = sorted(rows, key=_rank)[0]
            connection.execute(
                """
                UPDATE devices SET status='busy', current_run=?, busy_since=?,
                    last_assigned_at=?, last_heartbeat=?
                WHERE device_id=? AND status='online_idle'
                """,
                (run_id, now, now, now, chosen["device_id"]),
            )
        return self.get_device(chosen["device_id"])

    def release_device(self, device_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = str(payload.get("run_id") or "")
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT current_run FROM devices WHERE device_id=?", (device_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"device not found: {device_id}")
            if row["current_run"] and run_id and row["current_run"] != run_id:
                raise ValueError(f"device busy with another run: {row['current_run']}")
            connection.execute(
                """
                UPDATE devices SET status='online_idle', current_run='', busy_since=NULL,
                    last_heartbeat=?
                WHERE device_id=?
                """,
                (utc_now(), device_id),
            )
        return self.get_device(device_id)

    def set_device_status(self, device_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        status = str(payload.get("status") or "").strip()
        if status not in {"online_idle", "offline", "disabled"}:
            raise ValueError("status must be online_idle, offline or disabled")
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT status FROM devices WHERE device_id=?", (device_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"device not found: {device_id}")
            if row["status"] == "busy" and status != "disabled":
                raise ValueError("device is busy, release it first")
            connection.execute(
                "UPDATE devices SET status=?, last_heartbeat=? WHERE device_id=?",
                (status, utc_now(), device_id),
            )
        return self.get_device(device_id)

    # ---------- 流水线任务(P4):触发/认领/收尾 ----------

    def create_pipeline_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        trigger_source = str(payload.get("trigger_source") or "manual").strip()
        platform = str(payload.get("platform") or "flutter").strip().lower()
        if platform not in VALID_PLATFORMS:
            raise ValueError(f"platform must be one of {sorted(VALID_PLATFORMS)}")
        job_id = str(payload.get("job_id") or "").strip() or (
            f"job-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-"
            f"{uuid.uuid4().hex[:6]}"
        )
        with self.transaction() as connection:
            connection.execute(
                """
                INSERT INTO pipeline_jobs (
                    job_id, trigger_source, branch, platform, case_filter, apk_id,
                    status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
                """,
                (
                    job_id, trigger_source,
                    str(payload.get("branch") or "").strip(),
                    platform,
                    str(payload.get("case_filter") or "").strip(),
                    str(payload.get("apk_id") or "").strip() or None,
                    utc_now(),
                ),
            )
        return self.get_pipeline_job(job_id)

    def get_pipeline_job(self, job_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM pipeline_jobs WHERE job_id=?", (job_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"pipeline job not found: {job_id}")
        return self._serialize_pipeline_job(row)

    def list_pipeline_jobs(
        self, status: str = "", limit: int = 30
    ) -> list[dict[str, Any]]:
        with self.connect() as connection:
            if status:
                rows = connection.execute(
                    """SELECT * FROM pipeline_jobs WHERE status=?
                       ORDER BY created_at DESC LIMIT ?""",
                    (status, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM pipeline_jobs ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [self._serialize_pipeline_job(row) for row in rows]

    @staticmethod
    def _serialize_pipeline_job(row: sqlite3.Row) -> dict[str, Any]:
        item = dict(row)
        item["result"] = json.loads(item.pop("result_json") or "{}")
        return item

    def claim_pipeline_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        """执行 agent 认领最早的 pending 任务(原子操作,防多机抢跑)。"""
        claimed_by = str(payload.get("agent") or "").strip() or "unknown-agent"
        now = utc_now()
        with self.transaction() as connection:
            row = connection.execute(
                """SELECT job_id FROM pipeline_jobs WHERE status='pending'
                   ORDER BY created_at LIMIT 1"""
            ).fetchone()
            if row is None:
                raise LookupError("no pending pipeline job")
            job_id = row["job_id"]
            connection.execute(
                """UPDATE pipeline_jobs SET status='running', claimed_by=?,
                   claimed_at=?, attempts=attempts+1
                   WHERE job_id=? AND status='pending'""",
                (claimed_by, now, job_id),
            )
        return self.get_pipeline_job(job_id)

    def finish_pipeline_job(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        status = str(payload.get("status") or "").strip()
        valid = {"succeeded", "failed", "env_blocked", "error"}
        if status not in valid:
            raise ValueError(f"status must be one of {sorted(valid)}")
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT status FROM pipeline_jobs WHERE job_id=?", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"pipeline job not found: {job_id}")
            connection.execute(
                """UPDATE pipeline_jobs SET status=?, finished_at=?, result_json=?
                   WHERE job_id=?""",
                (status, utc_now(),
                 json.dumps(payload.get("result") or {}, ensure_ascii=False), job_id),
            )
        return self.get_pipeline_job(job_id)

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
        """按关键词模糊搜用例(取最近出现的 case_id),供历史页选择。

        keyword 为空时不加 WHERE,返回全部 case_id(页面默认展示全部,搜索后才过滤)。
        """
        limit = min(max(int(limit), 1), 100)
        pattern = f"%{keyword}%"
        with self.transaction() as connection:
            if keyword:
                rows = connection.execute(
                    """
                    SELECT c.case_id, MAX(c.name) AS name, COUNT(*) AS executions,
                           MAX(c.started_at) AS last_seen
                    FROM cases c WHERE c.case_id LIKE ?
                    GROUP BY c.case_id ORDER BY last_seen DESC LIMIT ?
                    """,
                    (pattern, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT c.case_id, MAX(c.name) AS name, COUNT(*) AS executions,
                           MAX(c.started_at) AS last_seen
                    FROM cases c
                    GROUP BY c.case_id ORDER BY last_seen DESC LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        return [dict(row) for row in rows]

    # ---- 用例定义(case_defs):文字用例 + 自动化脚本用例,双向关联 + bug 单来源 ----

    @staticmethod
    def _validate_case_def(payload: dict[str, Any], for_update: bool = False) -> dict[str, Any]:
        case_type = str(payload.get("case_type") or "").strip().lower()
        if case_type not in {"text", "auto"}:
            raise ValueError("case_type 必须是 text(文字用例) 或 auto(自动化脚本用例)")
        case_id = str(payload.get("case_id") or "").strip()
        if not case_id:
            raise ValueError("case_id 必填")
        fields = {
            "case_id": case_id,
            "case_type": case_type,
            "title": str(payload.get("title") or "").strip(),
            "module": str(payload.get("module") or "").strip(),
            "priority": str(payload.get("priority") or "").strip(),
            "source": str(payload.get("source") or "").strip(),
            "source_bug": str(payload.get("source_bug") or "").strip(),
            "file_path": str(payload.get("file_path") or "").strip(),
            "content": str(payload.get("content") or ""),
            "linked_case_id": str(payload.get("linked_case_id") or "").strip(),
        }
        if not fields["title"]:
            raise ValueError("title 必填")
        if fields["case_type"] == "auto" and fields["linked_case_id"] \
                and fields["linked_case_id"] == case_id:
            raise ValueError("linked_case_id 不能指向自己")
        return fields

    def upsert_case_def(self, payload: dict[str, Any]) -> dict[str, Any]:
        fields = self._validate_case_def(payload)
        now = utc_now()
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT case_id FROM case_defs WHERE case_id=?", (fields["case_id"],)
            ).fetchone()
            if row is None:
                connection.execute(
                    """INSERT INTO case_defs (
                        case_id, case_type, title, module, priority, source,
                        source_bug, file_path, content, linked_case_id,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (fields["case_id"], fields["case_type"], fields["title"],
                     fields["module"], fields["priority"], fields["source"],
                     fields["source_bug"], fields["file_path"], fields["content"],
                     fields["linked_case_id"], now, now),
                )
            else:
                connection.execute(
                    """UPDATE case_defs SET case_type=?, title=?, module=?,
                       priority=?, source=?, source_bug=?, file_path=?, content=?,
                       linked_case_id=?, updated_at=? WHERE case_id=?""",
                    (fields["case_type"], fields["title"], fields["module"],
                     fields["priority"], fields["source"], fields["source_bug"],
                     fields["file_path"], fields["content"], fields["linked_case_id"],
                     now, fields["case_id"]),
                )
        return self.get_case_def(fields["case_id"])

    def get_case_def(self, case_id: str) -> dict[str, Any]:
        item = self._get_case_def_row(case_id)
        return self._decorate_case_def(item)

    def _get_case_def_row(self, case_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM case_defs WHERE case_id=?", (case_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"用例定义不存在: {case_id}")
        return dict(row)

    def _decorate_case_def(self, item: dict[str, Any]) -> dict[str, Any]:
        """补双向关联视图:text 用例挂上指向它的 auto 用例;auto 用例挂上对应文字用例标题。"""
        with self.connect() as connection:
            if item["case_type"] == "text":
                autos = connection.execute(
                    """SELECT case_id, title, module, source_bug FROM case_defs
                       WHERE case_type='auto' AND linked_case_id=?
                       ORDER BY case_id""",
                    (item["case_id"],),
                ).fetchall()
                item["auto_cases"] = [dict(a) for a in autos]
            else:
                linked = connection.execute(
                    "SELECT case_id, title FROM case_defs WHERE case_id=?",
                    (item["linked_case_id"],),
                ).fetchone()
                item["text_case"] = dict(linked) if linked else None
        return item

    def list_case_defs(
        self, case_type: str = "", module: str = "", keyword: str = "",
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if case_type:
            clauses.append("case_type=?")
            params.append(case_type)
        if module:
            clauses.append("module=?")
            params.append(module)
        if keyword:
            pattern = f"%{keyword}%"
            clauses.append(
                "(case_id LIKE ? OR title LIKE ? OR module LIKE ? OR content LIKE ?)"
            )
            params.extend([pattern, pattern, pattern, pattern])
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        limit = min(max(int(limit), 1), 1000)
        with self.connect() as connection:
            rows = connection.execute(
                f"""SELECT case_id, case_type, title, module, priority, source,
                    source_bug, file_path, linked_case_id, updated_at
                    FROM case_defs{where} ORDER BY case_type, module, case_id
                    LIMIT ?""",
                (*params, limit),
            ).fetchall()
        # 列表视图一次性挂双向关联(text 行 -> auto_cases)
        autos: dict[str, list[dict[str, Any]]] = {}
        with self.connect() as connection:
            for row in connection.execute(
                """SELECT linked_case_id, case_id, title, module, source_bug
                   FROM case_defs WHERE case_type='auto' AND linked_case_id != ''
                   ORDER BY case_id"""
            ).fetchall():
                autos.setdefault(row["linked_case_id"], []).append(dict(row))
        items = []
        for row in rows:
            item = dict(row)
            if item["case_type"] == "text":
                item["auto_cases"] = autos.get(item["case_id"], [])
            items.append(item)
        return items

    def delete_case_def(self, case_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT case_id FROM case_defs WHERE case_id=?", (case_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"用例定义不存在: {case_id}")
            connection.execute("DELETE FROM case_defs WHERE case_id=?", (case_id,))
        return {"deleted": case_id}

    # ==================== 流水线配置(定时调度) ====================

    @staticmethod
    def _decorate_pipeline_config(row: sqlite3.Row) -> dict[str, Any]:
        """补实时字段:schedule(解析后的参数对象) + next_run_at(实时算,不落库)。"""
        item = dict(row)
        try:
            schedule = json.loads(item.get("schedule_param") or "{}")
        except json.JSONDecodeError:
            schedule = {}
        item["schedule"] = schedule if isinstance(schedule, dict) else {}
        item["next_run_at"] = compute_next_run_at(
            str(item.get("schedule_type") or ""), item.get("schedule_param") or "{}"
        )
        return item

    def create_pipeline_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        fields = validate_pipeline_config(payload)
        now = utc_now()
        with self.transaction() as connection:
            existing = connection.execute(
                "SELECT config_id FROM pipeline_configs WHERE config_id=?",
                (fields["config_id"],),
            ).fetchone()
            if existing is not None:
                raise ValueError(f"config_id 已存在: {fields['config_id']}")
            connection.execute(
                """INSERT INTO pipeline_configs (
                    config_id, name, description, suite_id, include_build,
                    schedule_type, schedule_param, enabled, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fields["config_id"], fields["name"], fields["description"],
                 fields["suite_id"], fields["include_build"], fields["schedule_type"],
                 fields["schedule_param"], fields["enabled"], now, now),
            )
        return self.get_pipeline_config(fields["config_id"])

    def get_pipeline_config(self, config_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM pipeline_configs WHERE config_id=?", (config_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"流水线配置不存在: {config_id}")
        return self._decorate_pipeline_config(row)

    def list_pipeline_configs(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM pipeline_configs ORDER BY config_id"
            ).fetchall()
        return [self._decorate_pipeline_config(row) for row in rows]

    def update_pipeline_config(self, config_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """部分更新:payload 未带的字段沿用库里现值,整体重新校验。"""
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM pipeline_configs WHERE config_id=?", (config_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"流水线配置不存在: {config_id}")
            merged = {
                "config_id": config_id,
                "name": payload.get("name", row["name"]),
                "description": payload.get("description", row["description"]),
                "suite_id": payload.get("suite_id", row["suite_id"]),
                "include_build": payload.get("include_build", row["include_build"]),
                "schedule_type": payload.get("schedule_type", row["schedule_type"]),
                "schedule_param": payload.get("schedule_param", row["schedule_param"]),
                "enabled": payload.get("enabled", row["enabled"]),
            }
            fields = validate_pipeline_config(merged)
            connection.execute(
                """UPDATE pipeline_configs SET name=?, description=?, suite_id=?,
                   include_build=?, schedule_type=?, schedule_param=?, enabled=?,
                   updated_at=? WHERE config_id=?""",
                (fields["name"], fields["description"], fields["suite_id"],
                 fields["include_build"], fields["schedule_type"],
                 fields["schedule_param"], fields["enabled"], utc_now(), config_id),
            )
        return self.get_pipeline_config(config_id)

    def delete_pipeline_config(self, config_id: str) -> dict[str, Any]:
        with self.transaction() as connection:
            row = connection.execute(
                "SELECT config_id FROM pipeline_configs WHERE config_id=?", (config_id,)
            ).fetchone()
            if row is None:
                raise KeyError(f"流水线配置不存在: {config_id}")
            connection.execute("DELETE FROM pipeline_configs WHERE config_id=?", (config_id,))
        return {"deleted": config_id}

    def run_pipeline_config(self, config_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """立即执行:照 trigger 通道建一个 schedule 来源任务,并回写 last_run_at。

        pipeline_jobs 的状态机/claim 逻辑不动;payload 可附带 platform/branch/
        case_filter/apk_id 覆盖(套件上线后由 suite_id 聚合,暂用这些字段)。
        """
        self.get_pipeline_config(config_id)  # 不存在抛 KeyError → 404
        job = self.create_pipeline_job({
            "trigger_source": "schedule",
            "platform": str(payload.get("platform") or "flutter"),
            "branch": str(payload.get("branch") or ""),
            "case_filter": str(payload.get("case_filter") or ""),
            "apk_id": str(payload.get("apk_id") or ""),
        })
        with self.transaction() as connection:
            connection.execute(
                "UPDATE pipeline_configs SET last_run_at=? WHERE config_id=?",
                (utc_now(), config_id),
            )
        return {"config": self.get_pipeline_config(config_id), "job": job}


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
            try:
                limit = int(query.get("limit", ["100"])[0])
            except ValueError:
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            # 未搜索状态展示全部用例,搜索后才返回匹配结果
            self.send_json({"items": self.store.search_case_ids(keyword, limit=limit)})
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
        if parsed.path == "/api/case-defs":
            query = parse_qs(parsed.query)
            try:
                limit = int(query.get("limit", ["200"])[0])
            except ValueError:
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": self.store.list_case_defs(
                case_type=query.get("type", [""])[0].strip(),
                module=query.get("module", [""])[0].strip(),
                keyword=query.get("q", [""])[0].strip(),
                limit=limit,
            )})
            return
        if parsed.path.startswith("/api/case-defs/"):
            case_id = parsed.path.removeprefix("/api/case-defs/").strip("/")
            try:
                self.send_json(self.store.get_case_def(case_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
            return
        if parsed.path == "/api/pipeline-configs":
            self.send_json({"items": self.store.list_pipeline_configs()})
            return
        if parsed.path.startswith("/api/pipeline-configs/"):
            config_id = parsed.path.removeprefix("/api/pipeline-configs/").strip("/")
            try:
                self.send_json(self.store.get_pipeline_config(config_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
            return
        if parsed.path == "/api/devices":
            self.send_json({"items": self.store.list_devices()})
            return
        if parsed.path == "/api/pipeline/jobs":
            query = parse_qs(parsed.query)
            status = query.get("status", [""])[0].strip()
            try:
                limit = int(query.get("limit", ["30"])[0])
            except ValueError:
                self.send_error_json("limit must be an integer", HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"items": self.store.list_pipeline_jobs(status=status, limit=limit)})
            return
        if parsed.path == "/api/zentao/config":
            from dashboard.zentao_client import is_configured
            self.send_json({
                "configured": is_configured(),
                "url": os.environ.get("ZENTAO_URL", ""),
            })
            return
        if parsed.path.startswith("/api/devices/"):
            device_id = parsed.path.removeprefix("/api/devices/").strip("/")
            try:
                self.send_json(self.store.get_device(device_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
            return
        if parsed.path.startswith("/api/pipeline/jobs/"):
            job_id = parsed.path.removeprefix("/api/pipeline/jobs/").strip("/")
            try:
                self.send_json(self.store.get_pipeline_job(job_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
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

    def zentao_draft(self, payload: dict[str, Any]) -> dict[str, Any]:
        """从失败用例生成禅道 bug 草稿(纯组装,不提交;提交走 /api/zentao/create)。"""
        run_id = str(payload.get("run_id") or "").strip()
        case_name = str(payload.get("case_name") or "").strip()
        if not run_id or not case_name:
            raise ValueError("run_id 和 case_name 必填")
        try:
            run = self.store.get_run(run_id)
        except KeyError as error:
            raise ValueError(str(error)) from error
        case = next((c for c in run.get("cases") or [] if c.get("name") == case_name), None)
        if case is None:
            raise ValueError(f"会话 {run_id} 中找不到用例 {case_name}")
        module = case_name.split(".py::")[0].rsplit("/", 1)[-1] if ".py::" in case_name else ""
        title = f"[Swan][{module or run['platform']}] {case_name.split('::')[-1]} 自动化失败({run_id})"
        steps_lines = [
            "【自动化复现步骤】",
            f"1. 执行会话 {run_id}(平台页可查,设备 {run.get('device') or '-'},包体 {run.get('apk_id') or '-'})",
            f"2. 用例: {case_name}",
            f"3. 实际结果: {case.get('status')} - {case.get('error') or '见执行日志'}",
            "",
            f"【执行日志摘要】",
            (case.get("log") or "无")[-1500:],
        ]
        artifacts = case.get("artifacts") or {}
        evidence_dir = artifacts.get("evidence_dir") or ""
        if evidence_dir:
            steps_lines.append(f"\n【逐步证据截图目录】{evidence_dir}")
        return {
            "title": title,
            "steps": "\n".join(steps_lines),
            "severity": 3,
            "pri": 3,
            "bug_type": "业务缺陷",
            "run_id": run_id,
            "case_name": case_name,
        }

    def read_optional_json(self) -> dict[str, Any]:
        """同 read_json,但允许空请求体(流水线"立即执行"类接口)。"""
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return self.read_json()

    def do_POST(self) -> None:
        try:
            parsed = urlparse(self.path)
            # 立即执行允许空请求体,须先于 read_json 分流(否则空 body 直接 400)
            if parsed.path.startswith("/api/pipeline-configs/") and parsed.path.endswith("/run"):
                config_id = parsed.path.removeprefix("/api/pipeline-configs/").removesuffix("/run").strip("/")
                self.send_json(
                    self.store.run_pipeline_config(config_id, self.read_optional_json()),
                    HTTPStatus.CREATED,
                )
                return
            payload = self.read_json()
            if parsed.path == "/api/runs":
                self.send_json(self.store.create_run(payload), HTTPStatus.CREATED)
                return
            if parsed.path == "/api/apks":
                self.send_json(self.store.register_apk(payload), HTTPStatus.CREATED)
                return
            if parsed.path == "/api/case-defs":
                self.send_json(self.store.upsert_case_def(payload), HTTPStatus.CREATED)
                return
            if parsed.path == "/api/pipeline-configs":
                self.send_json(self.store.create_pipeline_config(payload), HTTPStatus.CREATED)
                return
            if parsed.path == "/api/devices/register":
                self.send_json(self.store.register_device(payload), HTTPStatus.CREATED)
                return
            if parsed.path == "/api/devices/acquire":
                try:
                    self.send_json(self.store.acquire_device(payload), HTTPStatus.CREATED)
                except LookupError as error:
                    self.send_error_json(str(error), HTTPStatus.SERVICE_UNAVAILABLE)
                return
            if parsed.path == "/api/zentao/draft":
                self.send_json(self.zentao_draft(payload))
                return
            if parsed.path == "/api/zentao/create":
                from dashboard.zentao_client import ZentaoError, create_bug
                if not str(payload.get("confirm") or ""):
                    self.send_error_json("提单需人工确认(confirm 字段)", HTTPStatus.BAD_REQUEST)
                    return
                try:
                    result = create_bug(
                        product_id=int(payload["product_id"]),
                        title=str(payload["title"]),
                        steps=str(payload["steps"]),
                        severity=int(payload.get("severity") or 3),
                        pri=int(payload.get("pri") or 3),
                    )
                except (ZentaoError, KeyError, ValueError) as error:
                    self.send_error_json(str(error), HTTPStatus.BAD_GATEWAY)
                    return
                self.send_json(result, HTTPStatus.CREATED)
                return
            if parsed.path == "/api/pipeline/trigger":
                self.send_json(
                    self.store.create_pipeline_job(payload), HTTPStatus.CREATED
                )
                return
            if parsed.path == "/api/pipeline/claim":
                try:
                    self.send_json(self.store.claim_pipeline_job(payload))
                except LookupError as error:
                    self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
                return
            if parsed.path.startswith("/api/pipeline/jobs/") and parsed.path.endswith("/finish"):
                job_id = parsed.path.removeprefix("/api/pipeline/jobs/").removesuffix("/finish").strip("/")
                self.send_json(self.store.finish_pipeline_job(job_id, payload))
                return
            if parsed.path.startswith("/api/devices/") and parsed.path.endswith("/release"):
                device_id = parsed.path.removeprefix("/api/devices/").removesuffix("/release").strip("/")
                self.send_json(self.store.release_device(device_id, payload))
                return
            if parsed.path.startswith("/api/devices/") and parsed.path.endswith("/status"):
                device_id = parsed.path.removeprefix("/api/devices/").removesuffix("/status").strip("/")
                self.send_json(self.store.set_device_status(device_id, payload))
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


    def do_PUT(self) -> None:
        try:
            payload = self.read_json()
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/case-defs/"):
                case_id = parsed.path.removeprefix("/api/case-defs/").strip("/")
                if not case_id:
                    self.send_error_json("case_id is required", HTTPStatus.BAD_REQUEST)
                    return
                payload["case_id"] = case_id
                self.send_json(self.store.upsert_case_def(payload))
                return
            if parsed.path.startswith("/api/pipeline-configs/"):
                config_id = parsed.path.removeprefix("/api/pipeline-configs/").strip("/")
                if not config_id:
                    self.send_error_json("config_id is required", HTTPStatus.BAD_REQUEST)
                    return
                self.send_json(self.store.update_pipeline_config(config_id, payload))
                return
            self.send_error_json("not found", HTTPStatus.NOT_FOUND)
        except (ValueError, json.JSONDecodeError) as error:
            self.send_error_json(str(error), HTTPStatus.BAD_REQUEST)
        except KeyError as error:
            self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
        except Exception as error:
            self.send_error_json(str(error), HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/case-defs/"):
            case_id = parsed.path.removeprefix("/api/case-defs/").strip("/")
            if not case_id:
                self.send_error_json("case_id is required", HTTPStatus.BAD_REQUEST)
                return
            try:
                self.send_json(self.store.delete_case_def(case_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
            return
        if parsed.path.startswith("/api/pipeline-configs/"):
            config_id = parsed.path.removeprefix("/api/pipeline-configs/").strip("/")
            if not config_id:
                self.send_error_json("config_id is required", HTTPStatus.BAD_REQUEST)
                return
            try:
                self.send_json(self.store.delete_pipeline_config(config_id))
            except KeyError as error:
                self.send_error_json(str(error), HTTPStatus.NOT_FOUND)
            return
        self.send_error_json("not found", HTTPStatus.NOT_FOUND)


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
