"""关闭弹窗然后验证消息列表页"""
import sys
sys.path.insert(0, "E:\\UIAutotest")

from utils.aw import create_aw

aw = create_aw(platform="mumu", instance_id=0)

# 关闭浮窗弹窗
aw.click_text("取消", timeout=3)
aw.sleep(1)

# 确认在消息列表页
results = aw.ocr_scan_page()
texts = [r['text'] for r in results]

with open("explorer_output/state_check.txt", "w", encoding="utf-8") as f:
    f.write("After dismiss popup:\n")
    for t in texts:
        f.write(f"  {t}\n")
    f.write(f"\n'消息' visible: {'消息' in texts}")
