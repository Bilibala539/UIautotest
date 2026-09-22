"""流水线执行 agent(P4 步骤 11-12):在本机轮询平台领取任务并执行。

职责:
  1. 向平台 claim 一个 pending 任务(没有就退出/等待)
  2. 装包环节:任务指定 apk_id 时,执行用例前检查并安装被测包(失败按环境阻塞)
  3. 预检门禁:失败 → 任务标记 env_blocked(环境问题按 bug 处理,不计用例失败)
  4. 执行 pytest(PREFLIGHT=1 + EVIDENCE=1 + 设备池自动领取)
  5. 门禁重试(步骤 12):用例失败自动重跑一次(--lf 只跑失败项);
     重跑通过视为通过;环境阻塞不重跑、不计失败
  6. 把结果回报给平台(finish),运行记录/证据由 pytest_plugin 与证据体系落库

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
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
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
        # 装包环节已保证包就位;把包名传给 preflight,让 app_installed 检查生效
        env["SWAN_PACKAGE"] = _resolve_package()
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


def _finish_env_blocked(run_id: str, summary: str) -> dict:
    """环境阻塞收尾:pytest.exit(3)/装包失败都绕过 conftest 的 sessionfinish
    上报,run 记录会永远停在 running——这里补一条 error 收尾,保证终态一致。"""
    try:
        _post(f"/api/runs/{run_id}/complete", {
            "status": "error",
            "ended_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "summary": summary,
        })
    except RuntimeError as error:
        _log(f"WARNING run 收尾上报失败(执行会话可能停留 running): {error}")
    return {"status": "env_blocked", "result": {"run_id": run_id, "exit_code": 3}}


# 被测包名:装包检查与 preflight 的 app_installed 共用(SWAN_PACKAGE 可覆盖)
DEFAULT_SWAN_PACKAGE = "com.swan.network"
# 装包标记:设备侧记录最后一次成功安装的 apk_id,包变更时触发重装
APK_MARKER_PATH = "/data/local/tmp/swan_installed_apk_id.txt"


def _resolve_package() -> str:
    return os.environ.get("SWAN_PACKAGE", "").strip() or DEFAULT_SWAN_PACKAGE


def _adb_online_serials() -> list[str]:
    """当前 adb 在线(device 状态)的设备序列号。"""
    proc = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=15)
    return [parts[0] for line in proc.stdout.splitlines()[1:]
            if len(parts := line.split()) == 2 and parts[1] == "device"]


def _device_state(serial: str, package: str) -> tuple[bool, str]:
    """返回 (包是否已安装, 设备侧装包标记的 apk_id)。"""
    proc = subprocess.run(["adb", "-s", serial, "shell", "pm", "list", "packages", package],
                          capture_output=True, text=True, timeout=30)
    installed = package in proc.stdout
    marker = ""
    if installed:
        mark = subprocess.run(["adb", "-s", serial, "shell", "cat", APK_MARKER_PATH],
                              capture_output=True, text=True, timeout=15)
        marker = mark.stdout.strip()
    return installed, marker


def _download_apk(apk_id: str, dest: Path) -> Path:
    """从平台归档下载 APK 到本地缓存(dest),缓存已存在则直接复用。

    平台 download 端点自带两级回退(登记 file_path → 归档副本),跨机安全。
    """
    if dest.is_file() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        f"{PLATFORM_URL}/api/apks/{urllib.parse.quote(apk_id, safe='')}/download")
    tmp = dest.with_name(dest.name + ".part")
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            with open(tmp, "wb") as fh:
                while chunk := response.read(1024 * 1024):
                    fh.write(chunk)
        os.replace(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)
    return dest


# 安装确认弹窗适配:不同厂商路径不同(荣耀两道屏/小米授权框/…)。
# 只认控件属性与按钮文字,不写死坐标;新机型换确认路径时在此加规则即可
_INSTALL_POSITIVE_TEXT = ("继续安装", "继续", "仍要安装", "确定", "好", "OK")
_INSTALL_NEGATIVE_TEXT = ("取消", "应用市场", "商店")
_INSTALL_DIALOG_TIMEOUT = 900  # 传输+弹窗点通的总兜底(179MB 约 1 分钟)


def _ui_dump(serial: str) -> str:
    """当前界面的 uiautomator XML(界面忙碌时可能拿不到,返回空串由调用方重试)。"""
    for _ in range(2):
        dump = subprocess.run(
            ["adb", "-s", serial, "shell", "uiautomator", "dump", "/sdcard/swan_install_ui.xml"],
            capture_output=True, text=True, timeout=20)
        if dump.returncode == 0 and "ERROR" not in dump.stdout:
            cat = subprocess.run(["adb", "-s", serial, "shell", "cat", "/sdcard/swan_install_ui.xml"],
                                 capture_output=True, text=True, timeout=20)
            if "<node" in cat.stdout:
                return cat.stdout
        time.sleep(1)
    return ""


def _xml_attr(node: str, name: str) -> str:
    match = re.search(rf'{name}="([^"]*)"', node)
    return match.group(1) if match else ""


def _xml_center(node: str) -> tuple[int, int] | None:
    bounds = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", _xml_attr(node, "bounds"))
    if not bounds:
        return None
    x1, y1, x2, y2 = map(int, bounds.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def _pick_confirm_tap(xml: str) -> tuple[str, tuple[int, int]] | None:
    """从安装确认界面挑下一个该点的控件;不认识界面就返回 None(继续等)。

    顺序:先勾"已知晓风险"类勾选框,再点正向按钮;排除 取消/应用市场 类,
    避免把用户带去应用市场或点中广告位。
    """
    nodes = re.findall(r"<node[^>]*>", xml)
    # 1) 未勾选的勾选框(荣耀"已了解风险"/小米"我已知晓"等)
    for node in nodes:
        rid, cls, checked = _xml_attr(node, "resource-id"), _xml_attr(node, "class"), _xml_attr(node, "checked")
        if checked == "false" and (rid.endswith(":id/checkbox") or cls == "android.widget.CheckBox"):
            center = _xml_center(node)
            if center:
                return ("勾选风险确认框", center)
    # 2) 正向确认按钮
    for node in nodes:
        if _xml_attr(node, "clickable") != "true":
            continue
        text, rid = _xml_attr(node, "text"), _xml_attr(node, "resource-id")
        if any(bad in text for bad in _INSTALL_NEGATIVE_TEXT) or "offical" in rid or "market" in rid:
            continue
        if text in _INSTALL_POSITIVE_TEXT or (rid == "android:id/button1" and text):
            center = _xml_center(node)
            if center:
                return (f"点 {text or rid}", center)
    return None


def _install_apk(serial: str, apk_path: Path, apk_id: str) -> None:
    """install -r + 确认框自动点通:install 进程活着期间轮询界面,
    按 _pick_confirm_tap 规则逐屏点掉确认弹窗(不同厂商路径不同);
    全程只认控件属性/文字,不写死坐标。成功后写设备侧 apk_id 标记。"""
    proc = subprocess.Popen(
        ["adb", "-s", serial, "install", "-r", str(apk_path)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace")
    deadline = time.monotonic() + _INSTALL_DIALOG_TIMEOUT
    try:
        while True:
            try:
                out, _ = proc.communicate(timeout=4)
                break
            except subprocess.TimeoutExpired:
                pass
            if time.monotonic() > deadline:
                raise RuntimeError(f"安装确认超时({_INSTALL_DIALOG_TIMEOUT}s,弹窗未被自动点通)")
            tap = _pick_confirm_tap(_ui_dump(serial))
            if tap:
                label, (x, y) = tap
                _log(f"  [{serial}] 安装确认弹窗自动点掉: {label} @({x},{y})")
                subprocess.run(["adb", "-s", serial, "shell", "input", "tap", str(x), str(y)],
                               capture_output=True, text=True, timeout=15)
    finally:
        if proc.poll() is None:
            proc.kill()
            out = ""
    out = (out or "").strip()
    if proc.returncode != 0 or "Success" not in out:
        raise RuntimeError(f"adb install 失败: {out[-300:]}")
    # 装成功后写标记,下次同 apk_id 不重装(大包安装要 1-3 分钟)
    subprocess.run(["adb", "-s", serial, "shell", f"echo {apk_id} > {APK_MARKER_PATH}"],
                   capture_output=True, text=True, timeout=15)


def ensure_apk_installed(job: dict) -> str | None:
    """用例执行前的装包环节:job 指定 apk_id 时,确保在线真机装的是这个包。

    检查逻辑 = 包已安装 且 设备标记的 apk_id 与任务一致,否则安装 -r 重装
    (新构建包变更后自动换包)。返回 None=无需装包或全部成功;
    返回错误文案=环境阻塞(按 bug 处理,不计用例失败)。
    """
    apk_id = str(job.get("apk_id") or "").strip()
    if not apk_id:
        return None
    package = _resolve_package()
    serials = _adb_online_serials()
    if not serials:
        return "装包检查:无在线设备"
    try:
        apk_path = _download_apk(apk_id, PROJECT_ROOT / "output" / "apk_cache" / f"{apk_id}.apk")
    except Exception as error:  # noqa: BLE001 — 下载失败按环境阻塞处理
        return f"装包检查:APK {apk_id} 下载失败: {error}"
    _log(f"job={job.get('job_id')} 装包检查: apk={apk_id}"
         f"({apk_path.stat().st_size / 1048576:.0f}MB) package={package} devices={','.join(serials)}")
    errors = []
    for serial in serials:
        try:
            installed, marker = _device_state(serial, package)
            if installed and marker == apk_id:
                _log(f"  [{serial}] {package} 已是任务包({apk_id}),跳过安装")
                continue
            state = "包变更,重装" if installed else "未安装"
            _log(f"  [{serial}] {package} {state},开始安装(约 1-3 分钟)")
            _install_apk(serial, apk_path, apk_id)
            _log(f"  [{serial}] 安装成功")
        except Exception as error:  # noqa: BLE001 — 单设备失败汇总为环境阻塞
            errors.append(f"[{serial}] {error}")
    if errors:
        return "装包检查失败: " + "; ".join(errors)
    return None


def execute_job(job: dict) -> dict:
    """执行一个任务,返回 finish 载荷。门禁语义:
    - pytest 退出码 3(ENV_BLOCKED)→ env_blocked,不重跑不计失败
    - 退出码 1(有用例失败)→ 自动重跑一次(--lf);重跑通过=通过
    - 其他非零(收集错误/用法错误)→ error,不重跑
    """
    run_id = f"pipe-{job['job_id']}"
    # 步骤 2 装包环节:任务指定 apk_id 时,执行用例前确保真机装上该包;
    # 失败与门禁同语义,按环境阻塞处理(不重跑、不计用例失败)
    install_error = ensure_apk_installed(job)
    if install_error:
        _log(f"job={job['job_id']} ENV_BLOCKED(装包环节失败)")
        return _finish_env_blocked(run_id, install_error)
    first_rc = _run_pytest(job, run_id)
    if first_rc == 3:
        _log(f"job={job['job_id']} ENV_BLOCKED(环境门禁未过,按 bug 处理)")
        return _finish_env_blocked(run_id, "环境门禁未通过(env_blocked),未执行用例")
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
