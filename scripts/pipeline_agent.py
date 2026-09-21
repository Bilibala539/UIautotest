"""流水线执行 agent(P4 步骤 11-12):在本机轮询平台领取任务并执行。

职责:
  1. 向平台 claim 一个 pending 任务(没有就退出/等待)
  2. 预检门禁:失败 → 任务标记 env_blocked(环境问题按 bug 处理,不计用例失败)
  3. 执行 pytest(PREFLIGHT=1 + EVIDENCE=1 + 设备池自动领取)
  4. 门禁重试(步骤 12):用例失败自动重跑一次(--lf 只跑失败项);
     重跑通过视为通过;环境阻塞不重跑、不计失败
  5. 把结果回报给平台(finish),运行记录/证据由 pytest_plugin 与证据体系落库

触发双通道:
  - webhook:平台 POST /api/pipeline/trigger(供 git.hivi.com webhook 调用)
  - nightly:.166 计划任务每日凌晨 POST trigger(见 deploy 注释)

用法:
  python scripts/pipeline_agent.py --once      # 领一个任务执行完退出
  python scripts/pipeline_agent.py --loop 60   # 常驻轮询(默认 60 秒)
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 平台机缺省地址(v3:167 平台机,dashboard 同机);DASHBOARD_URL 可覆盖
PLATFORM_URL = os.environ.get("DASHBOARD_URL", "http://192.168.12.167:8080").rstrip("/")
# 平台未指定 case_filter 时的默认执行目标
DEFAULT_PYTEST_TARGET = "tests/flutter/test_case_driver.py"


def _load_dotenv_local() -> None:
    """加载项目根 .env.local(SWAN_PHONE/凭据等,部署机专属,不进 git)。

    Jenkins 以 SYSTEM 跑本脚本时没有交互会话的环境变量,pytest 侧
    (SWAN_PHONE/PLATFORM 判定等)依赖这里注入;已存在的环境变量优先。
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


def _post(path: str, payload: dict) -> dict:
    request = urllib.request.Request(
        f"{PLATFORM_URL}{path}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise RuntimeError(f"POST {path} -> HTTP {error.code}: {detail}") from error


def _log(message: str) -> None:
    print(f"[pipeline-agent {datetime.now(timezone.utc).isoformat(timespec='seconds')}] {message}", flush=True)


def _run_pytest(job: dict, run_id: str, rerun: bool = False) -> int:
    """跑一轮 pytest,返回 pytest 退出码(3=环境阻塞)。"""
    env = os.environ.copy()
    env.update({
        "PLATFORM": job.get("platform") or "flutter",
        "DASHBOARD_URL": PLATFORM_URL,
        "DASHBOARD_RUN_ID": run_id,
        "PREFLIGHT": "1",     # 门禁:环境阻塞 → pytest.exit(3)
        "EVIDENCE": "1",      # 每步标注截图
        "DEVICE_POOL": "1",   # 设备池自动领取/归还
    })
    # 包体透传:job 指定的 apk_id 交给上报插件(pytest_plugin 读 SWAN_APK_ID 落 runs.apk_id)。
    # job 未指定时主动清掉外层残留值,保证 run 的包关联严格等于任务指定的包
    if str(job.get("apk_id") or "").strip():
        env["SWAN_APK_ID"] = str(job["apk_id"]).strip()
    else:
        env.pop("SWAN_APK_ID", None)
    command = [sys.executable, "-m", "pytest"]
    target = job.get("case_filter") or DEFAULT_PYTEST_TARGET
    command.extend(target.split())
    if rerun:
        command.append("--lf")  # 只重跑上一轮失败项(pytest cache 内置)
    _log(f"job={job['job_id']} run={'rerun(--lf)' if rerun else 'first'} "
         f"target={target} platform={env['PLATFORM']}")
    # pythonw 常驻时无控制台,必须把子进程输出落文件,否则 pytest 崩溃(rc=1)
    # 用追加模式:重跑(--lf)不覆盖第一轮现场(门禁重试的排查依据)
    log_path = PROJECT_ROOT / "output" / "logs" / f"pipeline_{run_id}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n===== attempt {1 if not rerun else 2} "
                       f"({'--lf rerun' if rerun else 'first'}) "
                       f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} =====\n")
        result = subprocess.run(command, cwd=str(PROJECT_ROOT), env=env,
                                stdout=log_file, stderr=subprocess.STDOUT)
    return result.returncode


def execute_job(job: dict) -> dict:
    """执行一个任务,返回 finish 载荷。门禁语义:
    - pytest 退出码 3(ENV_BLOCKED)→ env_blocked,不重跑不计失败
    - 退出码 1(有用例失败)→ 自动重跑一次(--lf);重跑通过=通过
    - 其他非零(收集错误/用法错误)→ error,不重跑
    """
    run_id = f"pipe-{job['job_id']}"
    first_rc = _run_pytest(job, run_id)
    if first_rc == 3:
        _log(f"job={job['job_id']} ENV_BLOCKED(环境门禁未过,按 bug 处理)")
        # 门禁走 pytest.exit(3),绕过了 conftest 的 sessionfinish 上报,
        # run 记录会永远停在 running——这里补一条 error 收尾,保证执行会话终态一致
        try:
            _post(f"/api/runs/{run_id}/complete", {
                "status": "error",
                "ended_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "summary": "环境门禁未通过(env_blocked),未执行用例",
            })
        except RuntimeError as error:
            _log(f"WARNING run 收尾上报失败(执行会话可能停留 running): {error}")
        return {"status": "env_blocked", "result": {"run_id": run_id, "exit_code": 3}}
    if first_rc == 0:
        _log(f"job={job['job_id']} succeeded")
        return {"status": "succeeded", "result": {"run_id": run_id, "exit_code": 0}}
    if first_rc == 1:
        _log(f"job={job['job_id']} first run failed (rc=1), auto-rerun --lf")
        rerun_rc = _run_pytest(job, run_id, rerun=True)
        status = "succeeded" if rerun_rc == 0 else "failed"
        _log(f"job={job['job_id']} rerun rc={rerun_rc} -> {status}")
        return {"status": status, "result": {
            "run_id": run_id, "exit_code": rerun_rc,
            "rerun": True, "first_exit_code": 1,
        }}
    _log(f"job={job['job_id']} error (pytest rc={first_rc},收集/用法问题不重跑)")
    return {"status": "error", "result": {"run_id": run_id, "exit_code": first_rc}}


def process_once(job_id: str = "") -> bool:
    """领取并执行至多一个任务。返回是否领到了任务。

    job_id 提供时定向认领该任务(Jenkins 构建通道):任务不存在/已被认领/非
    pending 时平台 404 → 返回 False 优雅退出(不报错,构建置绿但不跑用例)。
    """
    # COMPUTERNAME 是 Windows 变量,Linux 回落 HOSTNAME/主机名
    agent = os.environ.get("COMPUTERNAME") or os.environ.get("HOSTNAME") or socket.gethostname()
    payload = {"agent": agent}
    if job_id:
        payload["job_id"] = job_id
    try:
        job = _post("/api/pipeline/claim", payload)
    except RuntimeError as error:
        if "404" in str(error):  # 无 pending 任务/定向任务不可认领——均属正常
            return False
        raise
    _log(f"claimed job={job['job_id']} source={job['trigger_source']} "
         f"branch={job['branch'] or '-'}")
    outcome = execute_job(job)
    try:
        _post(f"/api/pipeline/jobs/{job['job_id']}/finish", outcome)
    except RuntimeError as error:
        _log(f"WARNING 回报失败(任务结果留在本地日志): {error}")
    return True


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="流水线执行 agent")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="领一个任务执行完退出")
    mode.add_argument("--loop", type=int, metavar="SEC", help="常驻轮询,每 SEC 秒尝试领取")
    parser.add_argument("--job-id", help="定向认领指定任务(Jenkins 构建通道:执行完即退出)")
    args = parser.parse_args()

    if args.job_id:
        if not process_once(args.job_id):
            _log(f"job {args.job_id} 不可认领(不存在/已被认领/非 pending),按空跑退出")
        return 0
    if args.once:
        got = process_once()
        return 0
    if args.loop:
        _log(f"daemon 启动,轮询间隔 {args.loop}s,平台 {PLATFORM_URL}")
        while True:
            try:
                while process_once():
                    pass  # 把队列清空
            except Exception as error:  # noqa: BLE001 — 常驻进程单轮失败不退出
                _log(f"WARNING 单轮异常: {error}")
            time.sleep(args.loop)
    parser.error("需要 --once 或 --loop <秒>")
    return 2


if __name__ == "__main__":
    sys.exit(main())
