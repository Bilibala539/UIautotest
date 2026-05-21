"""
顺序执行 '会话列表及会话盒子.xlsx' 的「已实现 (50)」sheet 里的所有用例。

每跑完一条：
- 通过 → 在 Excel 的『ui自动化进度』列前缀加 '已通过 2026-05-20 - ' 并保留原值
- 失败 → 前缀加 '失败 2026-05-20 - ' 并保留原值
- 立即保存 Excel，防止崩溃丢数据
- 失败时把详细信息写到 logs/regression_failures.json

支持 --resume：跳过已经被标记 '已通过' 或 '失败 2026-05-20' 的行
支持 --only N1,N2: 只跑指定 row 号
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from openpyxl import load_workbook

PROJECT_ROOT = Path(r"E:\UIAutotest")
EXCEL = r"C:\Users\wb.menglingzhao02\Desktop\会话列表及会话盒子.xlsx"
SHEET = "已实现 (50)"
TEST_ROOT = PROJECT_ROOT / "tests" / "mumu"
PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
TODAY = datetime.date.today().isoformat()

FAIL_LOG = PROJECT_ROOT / "logs" / f"regression_failures_{datetime.date.today().isoformat()}.json"
PROGRESS_LOG = PROJECT_ROOT / "logs" / f"regression_progress_{datetime.date.today().isoformat()}.log"

# 标记
PASS_PREFIX = f"已通过 {TODAY} - "
FAIL_PREFIX = f"失败 {TODAY} - "


def load_cases():
    wb = load_workbook(EXCEL, data_only=True)
    ws = wb[SHEET]
    cases = []
    for r in range(2, ws.max_row + 1):
        text = ws.cell(r, 7).value
        if not text:
            continue
        m = re.search(r"(test_[^\s\(\)（）]+\.py)", str(text))
        if not m:
            continue
        cases.append({
            "row": r,
            "测试点": ws.cell(r, 3).value,
            "test_file": m.group(1),
            "progress_text": str(text),
        })
    wb.close()
    return cases


def locate_test(filename):
    candidates = list(TEST_ROOT.rglob(filename))
    return candidates[0] if candidates else None


def run_one(case, py_path):
    """跑单条用例，返回 (status, duration, stdout_tail, stderr_tail)"""
    start = time.time()
    rel = py_path.relative_to(PROJECT_ROOT)
    cmd = [
        str(PYTHON), "-m", "pytest",
        str(rel).replace("\\", "/"),
        "-v", "--tb=short",
        "--no-header",
        "-p", "no:cacheprovider",
        # 跳过 allure 上传以节省时间（不影响是否通过判断）
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    # 单机回归：注入 4 个用户键，避免 utils/distributed.py 的 get_node_users() 限制
    env["NODE_USERS"] = "userA,userB,userC,userD,grpmax,wangying43"

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=600,  # 10 分钟兜底
        )
        dur = time.time() - start
        # pytest exit code: 0 passed, 1 failed, 5 no tests collected
        status = "passed" if result.returncode == 0 else "failed"
        stdout_tail = result.stdout[-3000:] if result.stdout else ""
        stderr_tail = result.stderr[-1500:] if result.stderr else ""
        return status, dur, stdout_tail, stderr_tail, result.returncode
    except subprocess.TimeoutExpired:
        return "timeout", 600, "", "TIMEOUT after 600s", -1


def update_excel(row, status, original_text):
    """实时写回 Excel"""
    # 重新打开（每次都打开/保存，避免长时间持有句柄）
    wb = load_workbook(EXCEL)
    ws = wb[SHEET]
    if status == "passed":
        new_text = f"{PASS_PREFIX}{original_text}"
    else:
        new_text = f"{FAIL_PREFIX}{original_text}"
    ws.cell(row, 7).value = new_text
    wb.save(EXCEL)
    wb.close()


def is_already_processed(text):
    if not text:
        return False
    return (
        text.startswith(PASS_PREFIX)
        or text.startswith(FAIL_PREFIX)
        or text.startswith("已通过")
        or text.startswith("失败 ")
        or text.startswith("跳过 ")
    )


def log_progress(msg):
    line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    PROGRESS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", help="跳过已标记的行")
    parser.add_argument("--only", type=str, default=None, help="只跑指定的 row 号，逗号分隔，如 2,5,8")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要跑的内容，不实际执行")
    args = parser.parse_args()

    cases = load_cases()
    only_set = set(int(x) for x in args.only.split(",")) if args.only else None

    if args.resume:
        cases = [c for c in cases if not is_already_processed(c["progress_text"])]
    if only_set:
        cases = [c for c in cases if c["row"] in only_set]

    log_progress(f"准备执行 {len(cases)} 条用例")

    if args.dry_run:
        for c in cases:
            py = locate_test(c["test_file"])
            log_progress(f"  row{c['row']:>3}  {c['test_file']}  -> {py}")
        return

    failures = []
    if FAIL_LOG.exists():
        try:
            failures = json.loads(FAIL_LOG.read_text(encoding="utf-8"))
        except Exception:
            failures = []

    for i, c in enumerate(cases, 1):
        log_progress(f"--- ({i}/{len(cases)}) row{c['row']} 测试点={c['测试点']!r} 文件={c['test_file']}")
        py = locate_test(c["test_file"])
        if py is None:
            log_progress(f"  ❌ 找不到测试文件，标记为失败")
            update_excel(c["row"], "failed", "[文件缺失] " + c["progress_text"])
            failures.append({**c, "status": "missing_file", "stderr": ""})
            FAIL_LOG.write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")
            continue

        status, dur, stdout_tail, stderr_tail, rc = run_one(c, py)
        log_progress(f"  → {status} ({dur:.1f}s, rc={rc})")
        try:
            update_excel(c["row"], status, c["progress_text"])
        except Exception as e:
            log_progress(f"  ⚠️ 写回 Excel 失败：{e}")

        if status != "passed":
            failures.append({
                **c,
                "status": status,
                "duration": dur,
                "stdout_tail": stdout_tail,
                "stderr_tail": stderr_tail,
                "py_path": str(py),
            })
            FAIL_LOG.write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding="utf-8")

    # 统计
    total = len(cases)
    failed = len([f for f in failures if f["row"] in {c["row"] for c in cases}])
    log_progress(f"\n=== 完成 ===  总计 {total}，失败 {failed}，通过 {total - failed}")
    log_progress(f"失败详情：{FAIL_LOG}")


if __name__ == "__main__":
    main()
