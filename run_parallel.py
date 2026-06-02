"""
并行测试运行器 — 动态队列调度

架构：
  Coordinator (本脚本)
    ├─ 收集测试文件
    ├─ 预启动 N 台 MuMu 实例（可跳过）
    ├─ N 个 Worker 线程，每个绑定一个 INSTANCE_ID
    │     └─ 动态从队列领取文件，跑完一个领下一个
    └─ 汇总结果

用法：
  python run_parallel.py                        # 3 实例跑全量（不重装，与串行一致）
  python run_parallel.py -n 2                   # 2 实例
  python run_parallel.py -n 4 -t 10             # 4 实例跑前 10 个文件
  python run_parallel.py --reinstall             # 重装 APK 后再跑
  python run_parallel.py --branch release_4.23.0 # 指定分支并重装
  python run_parallel.py --no-setup             # 跳过设备启动（已手动开好）
"""

import argparse
import io
import os
import queue
import subprocess
import sys
import time
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import List, Optional

# ==================== 配置 ====================

TEST_DIR = Path("tests/checklist")
RESULTS_FILE = "parallel_results.json"

# ==================== 数据结构 ====================


@dataclass
class FileResult:
    file: str
    instance_id: int
    passed: int = 0
    failed: int = 0
    errors: int = 0
    duration: float = 0.0
    returncode: int = 0


@dataclass
class WorkerStats:
    instance_id: int
    files_run: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_errors: int = 0
    total_duration: float = 0.0
    results: List[FileResult] = field(default_factory=list)


# ==================== 收集测试 ====================


def collect_tests(limit: Optional[int] = None, file_list: Optional[List[str]] = None) -> List[str]:
    """收集测试文件，按文件名排序"""
    if file_list:
        return file_list

    if limit == 0:
        return []

    if not TEST_DIR.exists():
        print(f"错误: 测试目录不存在: {TEST_DIR}")
        sys.exit(1)

    files = sorted(str(f) for f in TEST_DIR.glob("test_*.py"))

    if not files:
        print(f"错误: 未找到测试文件: {TEST_DIR}/test_*.py")
        sys.exit(1)

    if limit:
        files = files[:limit]

    return files


# ==================== 解析 pytest 输出 ====================


def parse_pytest_output(output: str) -> tuple:
    """从 pytest 输出中解析 passed/failed/error 数量"""
    passed = failed = errors = 0

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        # pytest 结尾行格式: "= 3 passed, 1 failed, 1 error in 12.34s ="
        # 或 "= 3 passed in 5.67s ="
        if " passed" in line or " failed" in line or " error" in line:
            if "passed" in line:
                try:
                    idx = line.index("passed")
                    num_str = line[:idx].split()[-1]
                    passed = int(num_str)
                except (ValueError, IndexError):
                    pass
            if "failed" in line:
                try:
                    idx = line.index("failed")
                    num_str = line[:idx].split()[-1]
                    failed = int(num_str)
                except (ValueError, IndexError):
                    pass
            if "error" in line:
                try:
                    idx = line.index("error")
                    num_str = line[:idx].split()[-1]
                    errors = int(num_str)
                except (ValueError, IndexError):
                    pass

    return passed, failed, errors


# ==================== Worker ====================

print_lock = Lock()


def run_one_file(instance_id: int, test_file: str) -> FileResult:
    """在指定实例上运行单个测试文件"""
    env = os.environ.copy()
    env["INSTANCE_ID"] = str(instance_id)
    env["SKIP_SESSION_LOGIN"] = "1"
    env["SKIP_REPORT_UPLOAD"] = "1"
    env["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    # 并行模式：每个实例映射到不同账号，需要授权该账号
    _ACCOUNT_KEYS = ["userA", "userB", "userC", "userD"]
    if instance_id < len(_ACCOUNT_KEYS):
        env["NODE_USERS"] = _ACCOUNT_KEYS[instance_id]

    cmd = [
        sys.executable, "-m", "pytest",
        test_file,
        "-v", "--tb=short",
        "--no-header", "-q"
    ]

    start = time.time()
    try:
        result = subprocess.run(
            cmd, env=env,
            capture_output=True,
            encoding='utf-8', errors='replace',
            timeout=300,
            cwd=str(Path.cwd())
        )
        duration = time.time() - start
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        passed, failed, errors = parse_pytest_output(stdout + stderr)

        return FileResult(
            file=test_file,
            instance_id=instance_id,
            passed=passed,
            failed=failed,
            errors=errors,
            duration=duration,
            returncode=result.returncode
        )
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return FileResult(
            file=test_file,
            instance_id=instance_id,
            errors=1,
            duration=duration,
            returncode=-1
        )


def worker(instance_id: int, file_queue: queue.Queue, progress_callback) -> WorkerStats:
    """Worker 线程：持续从队列领取文件并执行"""
    stats = WorkerStats(instance_id=instance_id)

    while True:
        try:
            test_file = file_queue.get_nowait()
        except queue.Empty:
            break

        file_result = run_one_file(instance_id, test_file)
        stats.files_run += 1
        stats.total_passed += file_result.passed
        stats.total_failed += file_result.failed
        stats.total_errors += file_result.errors
        stats.total_duration += file_result.duration
        stats.results.append(file_result)

        progress_callback(instance_id, file_result)
        file_queue.task_done()

    return stats


# ==================== 设备启动 ====================


def setup_devices(count: int, branch: str = None, skip_install: bool = False):
    """预启动 MuMu 实例"""
    # Win+D 清桌面
    try:
        import pyautogui
        pyautogui.hotkey('win', 'd')
        time.sleep(0.5)
    except Exception:
        pass

    from utils.devices import start_devices, find_latest_apk_by_branch, \
        install_apk_to_all_devices, download_apk

    if skip_install:
        # 不重装 APK，仅启动设备并排列窗口
        from utils.devices import (
            is_mumu_running, close_all_mumu, start_emulator,
            get_adb_port, adb_connect, wait_device_ready, get_window_name,
            set_window_size_and_arrange, Device, CLOSE_WAIT, LAUNCH_WAIT,
            WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_GAP, MAX_DEVICES
        )
        from utils.window_manager import WindowManager

        count = min(max(1, count), MAX_DEVICES)
        devices = []

        if is_mumu_running():
            print("  检测到 MuMu 正在运行，正在关闭...")
            close_all_mumu()
            time.sleep(CLOSE_WAIT)

        print(f"  启动 {count} 台虚拟设备...")
        for i in range(count):
            if start_emulator(i):
                print(f"    实例 #{i} 启动中...")
            time.sleep(2)

        print(f"  等待启动 ({LAUNCH_WAIT}秒)...")
        time.sleep(LAUNCH_WAIT)

        for i in range(count):
            port = get_adb_port(i)
            addr = f"127.0.0.1:{port}"
            window_x = WINDOW_GAP + i * (WINDOW_WIDTH + WINDOW_GAP)
            window_name = get_window_name(i)
            is_ready = False
            if adb_connect(port):
                if wait_device_ready(port, timeout=30):
                    is_ready = True
                    print(f"    [OK] {addr} 就绪")
                else:
                    print(f"    [WARN] {addr} 未完全就绪")
            else:
                print(f"    [FAIL] {addr} 连接失败")

            devices.append(Device(
                instance_id=i, window_name=window_name,
                window_x=window_x, window_y=WINDOW_GAP,
                window_width=WINDOW_WIDTH, window_height=WINDOW_HEIGHT,
                adb_address=addr, adb_port=port, is_ready=is_ready
            ))

        set_window_size_and_arrange(count)
        for device in devices:
            WindowManager.focus_window(device.instance_id)
    else:
        # 正常模式：启动设备 + 安装 APK
        devices = start_devices(count)

        # 如果指定了分支，用分支查找最新包
        if branch:
            url, actual_branch, desc = find_latest_apk_by_branch(branch)
            if url:
                apk_path = download_apk(url)
                if apk_path:
                    install_apk_to_all_devices(devices, apk_path=apk_path)
            # 把 API 返回的实际分支名写入 env，供通知使用
            if actual_branch:
                os.environ["APK_BRANCH"] = actual_branch

    ready = sum(1 for d in devices if d.is_ready)
    if ready == 0:
        print("错误: 没有设备就绪，退出")
        sys.exit(1)

    print(f"  {ready}/{count} 台设备就绪")
    return devices


# ==================== 主流程 ====================


def main():
    parser = argparse.ArgumentParser(description="并行测试运行器（动态队列调度）")
    parser.add_argument("-n", "--instances", type=int, default=3,
                        help="MuMu 实例数 (默认 3)")
    parser.add_argument("-t", "--tests", type=int, default=None,
                        help="限制测试文件数 (默认全部)")
    parser.add_argument("--branch", type=str, default=None,
                        help="指定分支关键词查找最新 APK（自动触发 --reinstall）")
    parser.add_argument("--reinstall", action="store_true",
                        help="卸载旧版并重装 APK（默认不重装，与串行行为一致）")
    parser.add_argument("--no-setup", action="store_true",
                        help="跳过设备启动（假设已手动开好）")
    parser.add_argument("--files", nargs="*", default=None,
                        help="指定要运行的测试文件列表（替代自动收集）")
    parser.add_argument("--file-list", type=str, default=None,
                        help="从文本文件读取测试文件列表（每行一个路径）")
    args = parser.parse_args()

    n_instances = args.instances

    # 1. 收集测试文件
    file_list = args.files
    if args.file_list:
        with open(args.file_list, "r", encoding="utf-8") as f:
            file_list = [line.strip() for line in f if line.strip()]
    test_files = collect_tests(args.tests, file_list=file_list)
    print("=" * 60)
    if test_files:
        print(f"  并行测试: {len(test_files)} 个文件 → {n_instances} 个实例 (动态队列)")
    else:
        print(f"  仅启动设备（不执行用例）")
    print("=" * 60)

    # 2. 启动设备
    if args.no_setup:
        print("\n跳过设备启动 (--no-setup)")
    elif args.reinstall or args.branch:
        print("\n启动 MuMu 实例 + 重装 APK...")
        setup_devices(n_instances, branch=args.branch)
        print("  下次如需跳过重装，去掉 --reinstall/--branch 即可")
    else:
        print("\n启动 MuMu 实例 (不重装，与串行一致)...")
        setup_devices(n_instances, skip_install=True)

    # 若 setup_devices 未写入 APK_BRANCH（skip_install / no-setup 情形），用默认值兜底
    if not os.environ.get("APK_BRANCH"):
        from utils.devices import APK_BRANCH as _DEFAULT_APK_BRANCH
        os.environ["APK_BRANCH"] = _DEFAULT_APK_BRANCH

    if not test_files:
        print("\n  设备已就绪，无测试文件需要执行")
        return

    # 3. 填充队列

    # 3. 填充队列
    file_queue = queue.Queue()
    for f in test_files:
        file_queue.put(f)

    # 4. 进度回调
    completed_count = 0
    total_files = len(test_files)
    progress_lock = Lock()

    def on_file_done(instance_id: int, result: FileResult):
        nonlocal completed_count
        with progress_lock:
            completed_count += 1
            status = "✅" if result.returncode == 0 else "❌"
            short_name = Path(result.file).stem
            print(f"  [{completed_count}/{total_files}] {status} 实例#{instance_id} "
                  f"{short_name} ({result.passed}✓ {result.failed}✗ {result.errors}E "
                  f"{result.duration:.1f}s)")

    # 5. 并行执行
    print(f"\n{'=' * 60}")
    print(f"  执行中...")
    print(f"{'=' * 60}")

    overall_start = time.time()
    all_stats: List[WorkerStats] = []

    with ThreadPoolExecutor(max_workers=n_instances) as executor:
        futures = {
            executor.submit(worker, i, file_queue, on_file_done): i
            for i in range(n_instances)
        }
        for future in as_completed(futures):
            stats = future.result()
            all_stats.append(stats)

    overall_duration = time.time() - overall_start

    # 6. 汇总
    all_stats.sort(key=lambda s: s.instance_id)
    total_passed = sum(s.total_passed for s in all_stats)
    total_failed = sum(s.total_failed for s in all_stats)
    total_errors = sum(s.total_errors for s in all_stats)

    print(f"\n{'=' * 60}")
    print(f"  结果汇总")
    print(f"{'=' * 60}")
    print(f"  总用例: {total_passed + total_failed + total_errors}")
    print(f"  通过:   {total_passed} ✅")
    print(f"  失败:   {total_failed} ❌")
    print(f"  错误:   {total_errors} ⚠️")
    print(f"  总耗时: {overall_duration:.1f}s")
    print()

    max_duration = max((s.total_duration for s in all_stats), default=0)
    print(f"  各实例:")
    for s in all_stats:
        pct = (s.total_duration / max_duration * 100) if max_duration > 0 else 0
        print(f"    实例#{s.instance_id}: {s.files_run}文件, "
              f"{s.total_passed}✓ {s.total_failed}✗ {s.total_errors}E, "
              f"{s.total_duration:.1f}s ({pct:.0f}%)")

    # 7. 写结果文件
    results_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "instances": n_instances,
        "total_files": total_files,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "overall_duration_s": round(overall_duration, 1),
        "workers": [
            {
                "instance_id": s.instance_id,
                "files_run": s.files_run,
                "passed": s.total_passed,
                "failed": s.total_failed,
                "errors": s.total_errors,
                "duration_s": round(s.total_duration, 1),
                "files": [
                    {
                        "file": r.file,
                        "passed": r.passed,
                        "failed": r.failed,
                        "errors": r.errors,
                        "duration_s": round(r.duration, 1),
                    }
                    for r in s.results
                ]
            }
            for s in all_stats
        ]
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    print(f"\n  结果已写入: {RESULTS_FILE}")

    # 8. 合并上传测试结果（一条记录）
    upload_combined_session(results_data, n_instances, all_stats)

    # 9. 退出码
    if total_failed > 0 or total_errors > 0:
        sys.exit(1)


def upload_combined_session(results_data: dict, n_instances: int,
                            all_stats: List[WorkerStats]):
    """合并所有实例的 session 数据为一条记录，统一上传"""
    import socket
    import shutil

    base_dir = str(Path.cwd())
    sessions_dir = os.path.join(base_dir, "output", "sessions")

    # 收集各实例保存的 session.json（每个文件一个独立 session）
    instance_sessions = []
    if os.path.isdir(sessions_dir):
        for d in sorted(os.listdir(sessions_dir)):
            session_file = os.path.join(sessions_dir, d, "session.json")
            if os.path.isfile(session_file):
                # 从目录名提取实例 ID（格式: YYYYMMDD_HHMMSS_inst{N}）
                parts = d.rsplit("_inst", 1)
                if len(parts) == 2:
                    try:
                        inst_id = int(parts[1])
                    except ValueError:
                        continue
                    with open(session_file, "r", encoding="utf-8") as f:
                        instance_sessions.append((inst_id, d, json.load(f)))

    # 合并 tests 列表，标记来源实例
    all_tests = []
    for inst_id, dir_name, sess in instance_sessions:
        for t in sess.get("tests", []):
            t["instance_id"] = inst_id
            all_tests.append(t)

    # 构造合并的 session
    session_id = time.strftime('%Y%m%d_%H%M%S') + "_parallel"
    combined_session = {
        "id": session_id,
        "ts": results_data["timestamp"],
        "platform": "Android",
        "project": "POPO-Android",
        "host": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "total": results_data["total_passed"] + results_data["total_failed"] + results_data["total_errors"],
        "passed": results_data["total_passed"],
        "failed": results_data["total_failed"],
        "skipped": 0,
        "duration": results_data["overall_duration_s"],
        "parallel": True,
        "instances": n_instances,
        "workers": [
            {
                "instance_id": s.instance_id,
                "files_run": s.files_run,
                "passed": s.total_passed,
                "failed": s.total_failed,
                "errors": s.total_errors,
                "duration_s": round(s.total_duration, 1),
            }
            for s in all_stats
        ],
        "tests": all_tests,
    }

    # 保存合并的 session 到本地
    combined_dir = os.path.join(sessions_dir, session_id)
    os.makedirs(combined_dir, exist_ok=True)

    # 收集各实例的日志文件到合并目录
    logs_dst = os.path.join(combined_dir, "logs")
    os.makedirs(logs_dst, exist_ok=True)
    for inst_id, dir_name, _ in instance_sessions:
        inst_logs = os.path.join(sessions_dir, dir_name, "logs")
        if os.path.isdir(inst_logs):
            for f in os.listdir(inst_logs):
                src = os.path.join(inst_logs, f)
                dst = os.path.join(logs_dst, f"inst{inst_id}_{f}")
                shutil.copy2(src, dst)

    with open(os.path.join(combined_dir, "session.json"), "w", encoding="utf-8") as f:
        json.dump(combined_session, f, ensure_ascii=False, indent=2)

    # 上传
    try:
        import paramiko
        from scp import SCPClient

        _REPORT_HOST = "10.220.28.125"
        _REPORT_USER = "popoqa91"
        _REPORT_PASS = "123456"
        _REPORT_REMOTE_DIR = "/var/www/html/reports"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(_REPORT_HOST, username=_REPORT_USER, password=_REPORT_PASS, timeout=30)

        # 确保远端目录存在
        ssh.exec_command(f"mkdir -p {_REPORT_REMOTE_DIR}/sessions")

        # 上传合并的 session 目录
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(combined_dir, f"{_REPORT_REMOTE_DIR}/sessions", recursive=True)

        # 同步远端 index.json
        sftp = ssh.open_sftp()
        _sync_parallel_to_remote(sftp, combined_session, _REPORT_REMOTE_DIR)
        sftp.close()

        ssh.close()
        print(f"\n  ✅ 测试结果已上传 (会话: {session_id})")

        # 清理本地 sessions 目录
        if os.path.isdir(sessions_dir):
            shutil.rmtree(sessions_dir, ignore_errors=True)

    except Exception as e:
        print(f"\n  ⚠️ 结果上传失败: {e}")


def _sync_parallel_to_remote(sftp, session_data: dict, remote_base: str):
    """将合并的并行 session 同步到远端 index.json + test_history.json"""
    import io

    remote_dir = f"{remote_base}/sessions"
    sid = session_data["id"]

    def _download_json(remote_path, default):
        try:
            with sftp.open(remote_path, "r") as f:
                return json.loads(f.read().decode("utf-8"))
        except Exception:
            return default

    def _upload_json(remote_path, data):
        buf = io.BytesIO(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        sftp.putfo(buf, remote_path)

    # 更新 index.json
    index = _download_json(f"{remote_dir}/index.json", {"sessions": []})
    index["sessions"] = [s for s in index["sessions"] if s["id"] != sid]
    index["sessions"].insert(0, {
        k: session_data[k]
        for k in ("id", "ts", "platform", "project", "host", "ip",
                  "total", "passed", "failed", "skipped", "duration")
        if k in session_data
    })
    # 标记并行
    index["sessions"][0]["parallel"] = True
    index["sessions"][0]["instances"] = session_data.get("instances", 1)
    _upload_json(f"{remote_dir}/index.json", index)

    # 更新 test_history.json
    hist = _download_json(f"{remote_dir}/test_history.json", {})
    for t in session_data.get("tests", []):
        key = t.get("name", t.get("file", "unknown"))
        if key not in hist:
            hist[key] = []
        hist[key].append({
            "session_id": sid,
            "platform": "Android",
            "status": t.get("status", "error"),
            "duration": t.get("duration", 0),
            "log": t.get("log", ""),
            "instance_id": t.get("instance_id", 0),
        })
    _upload_json(f"{remote_dir}/test_history.json", hist)


if __name__ == "__main__":
    main()
