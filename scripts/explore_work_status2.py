"""探索工作状态 - 通过侧边栏头像进入"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)

# Current state: sidebar is open, we can see 孟静娴 at [82,204]
# Try clicking on the avatar/name area (the avatar should be to the left of the name)
print("Step 2: Click on user avatar area in sidebar...")
aw.tap(30, 204)  # Avatar area (left of name)
time.sleep(2)

result = aw.ocr_scan_page()
print("\nAfter clicking avatar:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Check for status-related options
status_kw = ['工作状态', '在线', '忙碌', '离开', '请勿打扰', '隐身', '状态', '设置状态', '编辑资料']
for r in result:
    for kw in status_kw:
        if kw in r['text']:
            print(f"\n  *** Found: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/work_status_step2.png')
