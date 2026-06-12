import json
import subprocess
import sys
import tempfile
import os
from datetime import datetime
from pathlib import Path

results_file = Path(__file__).parent.parent / "parallel_results.json"

if not results_file.exists():
    print("parallel_results.json 不存在，跳过发送")
    sys.exit(0)

# 检查结果文件是否是本次跑出来的（5分钟内写入）
file_age_minutes = (datetime.now().timestamp() - results_file.stat().st_mtime) / 60
if file_age_minutes > 5:
    print(f"parallel_results.json 已有 {file_age_minutes:.0f} 分钟未更新，本次测试未正常完成，跳过发送")
    sys.exit(1)

with open(results_file, encoding="utf-8") as f:
    data = json.load(f)

passed    = data.get("total_passed", 0)
failed    = data.get("total_failed", 0)
errors    = data.get("total_errors", 0)
total     = passed + failed + errors
pct       = f"{passed / total * 100:.1f}" if total > 0 else "0.0"
dur_s     = data.get("overall_duration_s", 0)
dur_min   = int(dur_s // 60)
n_inst    = data.get("instances", 3)
date_str  = datetime.now().strftime("%Y-%m-%d")
session_id = data.get("session_id", "")

if session_id:
    report_url = f"http://10.220.28.125/reports/allure-report/history.html#s/{session_id}"
else:
    report_url = "http://10.220.28.125/reports"

msg = f"""UIAutotest 夜间测试报告（{date_str}）

环境：MuMu 模拟器 × {n_inst} 台并行
范围：tests/checklist 全量 {total} 个用例

结果：
• 通过：{passed}（{pct}%）
• 失败：{failed + errors}
耗时：{dur_s:.0f}s（约 {dur_min} 分钟）
测试详情：{report_url}"""

with tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                  delete=False, encoding="utf-8") as f:
    f.write(msg)
    tmpfile = f.name

try:
    POPO_CLI = r"C:\Users\wb.menglingzhao02\AppData\Roaming\npm\popo-cli.cmd"
    subprocess.run(
        [POPO_CLI, "popo", "message_send_team",
         f"message=@text:{tmpfile}", "receiver=3220461", "source=AGENT"],
        check=True
    )
    print("POPO 群消息发送成功")
    sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
finally:
    os.unlink(tmpfile)
