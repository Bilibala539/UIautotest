import datetime
import json
from pathlib import Path

today = datetime.date.today().isoformat()
failure_path = Path(rf'E:\UIAutotest\logs\regression_failures_{today}.json')
data = json.load(open(failure_path, encoding='utf-8'))
out = [f'失败用例数: {len(data)}']
for i, f in enumerate(data):
    out.append(f'\n--- #{i+1} row{f["row"]} {f["test_file"]} ---')
    out.append(f'测试点: {f.get("测试点")}')
    out.append(f'status: {f.get("status")}')
    out.append(f'duration: {f.get("duration")}')
    out.append('stderr_tail:')
    out.append((f.get("stderr_tail", "") or "")[-1500:])
    out.append('stdout_tail:')
    out.append((f.get("stdout_tail", "") or "")[-2000:])

Path(r'E:\UIAutotest\logs\fail_summary_current.txt').write_text("\n".join(out), encoding='utf-8')
print('written')
