"""
对那 22 条只显示 'AssertionError' 的失败，从 stdout_tail 里抽更多上下文。
"""
import datetime
import json
import re
from pathlib import Path

today = datetime.date.today().isoformat()
data = json.load(open(rf'E:\UIAutotest\logs\regression_failures_{today}.json', encoding='utf-8'))

# 22 条没有 reason 的: 把 stdout_tail 最后 30 行打印出来
TARGET_ROWS = {10,11,12,13,14,15,16,18,19,25,26,27,28,29,30,37,38,39,40,41,47,48}
out = []
for f in data:
    if f['row'] not in TARGET_ROWS:
        continue
    out.append(f"\n========== row{f['row']} {f['test_file']} 测试点={f.get('测试点')} ==========")
    stdout = f.get('stdout_tail', '') or ''
    # 抽 'FAILED' / 'AssertionError' 附近 30 行
    lines = stdout.splitlines()
    # 找 FAILED 行
    fail_idx = None
    for i, l in enumerate(lines):
        if 'FAILED ' in l or '❌' in l:
            fail_idx = i
            break
    if fail_idx is None:
        fail_idx = len(lines) - 1
    start = max(0, fail_idx - 25)
    out.extend(lines[start:fail_idx + 5])

Path(rf'E:\UIAutotest\logs\fail_details_assertonly.txt').write_text("\n".join(out), encoding='utf-8')
print('written')
