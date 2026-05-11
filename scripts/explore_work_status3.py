"""探索工作状态 - 尝试更多入口"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)

# Go back to message page
print("Going back...")
aw.press_back()
time.sleep(1)
aw.press_back()
time.sleep(2)

# Now check the message list header area
# The sidebar had "工卡" text at [389,206] - maybe that's related?
# Also, let's look at "更多" tab for work status
print("Step 3: Click '更多' tab...")
aw.click_text("更多", timeout=10)
time.sleep(2)

result = aw.ocr_scan_page()
print("\n'更多' page elements:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Look for work status
status_kw = ['工作状态', '状态', '在线', '忙碌']
for r in result:
    for kw in status_kw:
        if kw in r['text']:
            print(f"\n  *** Found: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/more_tab_page.png')
