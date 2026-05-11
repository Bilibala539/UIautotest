"""探索工作状态 - 使用知识库中记录的坐标"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# Force stop and restart
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'am', 'force-stop', POPO_PACKAGE], capture_output=True)
time.sleep(2)
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(10)

# Open sidebar
print("Step 1: Open sidebar...")
aw.tap(27, 71)  # Top-left avatar
time.sleep(2)

# Take screenshot of sidebar to verify
img = aw.take_screenshot(save_path='explorer_output/screenshots/sidebar_workstatus_v2.png')

# According to knowledge base, "工作状态" is at [394, 129] in sidebar
print("\nStep 2: Click 工作状态 at (394, 129)...")
aw.tap(394, 129)
time.sleep(2)

# OCR scan the new page
result = aw.ocr_scan_page()
print("\nAfter clicking work status area:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Look for work status options
status_kw = ['工作状态', '在线', '忙碌', '离开', '请勿打扰', '隐身', '状态', '会议中', 
             '休息', '外出', '出差', '设置', '清除']
print("\n--- Status keywords found: ---")
for r in result:
    for kw in status_kw:
        if kw in r['text']:
            print(f"  Found \"{kw}\" in \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/work_status_page.png')
