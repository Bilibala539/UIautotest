"""dispatch_worker 通道选择联测(2026-09-30):167 SSH 化 + wecom 回退链。

纪律:全程 fake _run,绝不真调 ssh/tmux;STUB=1 全流程不碰 ssh/tmux 由
test_dispatch_worker_stub.py 保证,这里单测路由选择逻辑本身。
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path

WORKER_PATH = Path(__file__).resolve().parents[2] / "scripts" / "dispatch_worker.py"


def _load_worker():
    """以 STUB=1 安全默认加载 worker 模块(纯定义,无副作用),测试内再改属性。"""
    spec = importlib.util.spec_from_file_location("dispatch_worker_routes", WORKER_PATH)
    module = importlib.util.module_from_spec(spec)
    old = os.environ.get("DISPATCH_STUB")
    os.environ["DISPATCH_STUB"] = "1"
    try:
        spec.loader.exec_module(module)
    finally:
        if old is None:
            os.environ.pop("DISPATCH_STUB", None)
        else:
            os.environ["DISPATCH_STUB"] = old
    return module


class _FakeCompleted:
    def __init__(self, returncode: int = 0, stdout: bytes = b"", stderr: bytes = b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_run(calls: list):
    def run(args, input_bytes=None, timeout=30):
        calls.append((args, input_bytes))
        return _FakeCompleted()
    return run


def _task(machine: str) -> dict:
    return {"task_id": "TASK-20260930-001", "title": "修选择器", "submitter": "yumiao",
            "task_type": "test_run", "target_machine": machine}


def test_route_167_via_ssh_when_configured():
    worker = _load_worker()
    worker.STUB = False
    worker.SSH_167 = "jks@127.0.0.1"
    calls: list = []
    worker._run = _fake_run(calls)

    assert worker._ssh_host_for("167") == "jks@127.0.0.1"
    assert ("167", "jks@127.0.0.1") in worker._remote_hosts()  # outbox 回读同构
    assert worker.dispatch_task(_task("167"), None, None) is True

    (args, body), = calls  # 一条 SSH 会话:远端 inbox 文件 + jks 身份的 tmux 按键
    assert args[0] == "ssh" and args[1] == "jks@127.0.0.1"
    assert "tmux send-keys" in args[2] and "$HOME/leader/inbox/" in args[2]
    assert json.loads(body.decode("utf-8"))["task_id"] == "TASK-20260930-001"


def test_route_167_local_when_unset():
    worker = _load_worker()
    worker.STUB = False
    worker.SSH_167 = ""
    calls: list = []
    worker._run = _fake_run(calls)
    with tempfile.TemporaryDirectory() as temporary_directory:
        worker.INBOX_DIR = Path(temporary_directory) / "inbox"

        assert worker._ssh_host_for("167") is None
        assert not [machine for machine, _ in worker._remote_hosts() if machine == "167"]
        assert worker.dispatch_task(_task("167"), None, None) is True

        (args, _), = calls  # 本地直连:本地 tmux,不碰 ssh
        assert args[0] == "tmux" and args[1] == "send-keys"
        assert not any(args[0] == "ssh" for args, _ in calls)
        inbox_file, = worker.INBOX_DIR.glob("*.json")
        assert json.loads(inbox_file.read_text(encoding="utf-8"))["task_id"] == "TASK-20260930-001"


def test_route_176_always_ssh():
    worker = _load_worker()
    worker.STUB = False
    worker.SSH_167 = ""  # 176 通道不受 167 配置影响
    calls: list = []
    worker._run = _fake_run(calls)

    assert worker._ssh_host_for("176") == worker.MACHINE_SSH["176"]
    assert worker.dispatch_task(_task("176"), None, None) is True
    (args, _), = calls
    assert args[0] == "ssh" and args[1] == worker.MACHINE_SSH["176"]


def test_outbox_readback_mirrors_dispatch_channel():
    worker = _load_worker()
    worker.STUB = False
    worker.SSH_167 = "jks@127.0.0.1"
    report = json.dumps({"task_id": "TASK-20260930-001", "phase": "progress",
                         "detail": "x"}, ensure_ascii=False).encode("utf-8")
    calls: list = []

    def run(args, input_bytes=None, timeout=30):
        calls.append(args)
        if "ls -1" in args[2]:
            return _FakeCompleted(stdout=b"/home/jks/leader/outbox/1-TASK-20260930-001.json\n")
        return _FakeCompleted(stdout=report)  # cat

    worker._run = run
    with tempfile.TemporaryDirectory() as temporary_directory:
        worker.OUTBOX_DIR = Path(temporary_directory) / "outbox"  # 本地空,只剩远端
        items = list(worker._iter_outbox())
    assert len(items) == 2  # 176 + 167 各一次远端扫描
    sources = {source for source, _, _ in items}
    assert sources == {f"176:{worker.MACHINE_SSH['176']}", "167:jks@127.0.0.1"}
    assert items[0][2] == report.decode("utf-8")

    # 清理同样按来源走对应 SSH 主机
    worker._run = _fake_run(calls)
    worker._discard_outbox("167:jks@127.0.0.1", "1-TASK-20260930-001.json")
    last_args = calls[-1][0]
    assert last_args[0] == "ssh" and last_args[1] == "jks@127.0.0.1"
    assert "rm -f" in last_args[2]


def test_wecom_fallback_chain(monkeypatch):
    worker = _load_worker()
    monkeypatch.setattr("shutil.which", lambda name: None)  # 本机没有 wecom-cli
    calls: list = []

    # 默认回退 .176(生产 worker 在 .167 上,ssh 回自己只会卡死)
    def probe_ok(args, input_bytes=None, timeout=30):
        calls.append(args)
        return _FakeCompleted(stdout=b"/usr/local/bin/wecom-cli\n")

    worker._run = probe_ok
    assert worker.wecom_cli_command() == ["ssh", worker.MACHINE_SSH["176"],
                                          "/usr/local/bin/wecom-cli"]
    assert calls[-1][1] == worker.MACHINE_SSH["176"]

    # DISPATCH_SSH_WECOM 覆盖回退机
    monkeypatch.setenv("DISPATCH_SSH_WECOM", "me@somewhere")
    calls.clear()
    assert worker.wecom_cli_command() == ["ssh", "me@somewhere", "/usr/local/bin/wecom-cli"]
    assert calls[-1][1] == "me@somewhere"

    # 本机有 wecom-cli → 直接本机,不碰 ssh
    monkeypatch.setattr("shutil.which", lambda name: "/usr/local/bin/wecom-cli"
                        if name == "wecom-cli" else None)
    calls.clear()
    assert worker.wecom_cli_command() == ["wecom-cli"]
    assert not calls

    # 探测失败(命令不存在/超时)→ None,调用方降级只记事件
    monkeypatch.setattr("shutil.which", lambda name: None)
    worker._run = lambda args, input_bytes=None, timeout=30: _FakeCompleted(returncode=1)
    assert worker.wecom_cli_command() is None

    def raise_timeout(args, input_bytes=None, timeout=30):
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)

    worker._run = raise_timeout
    assert worker.wecom_cli_command() is None
