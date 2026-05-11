"""探索设置工作状态功能"""
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

# 工作状态入口通常在侧边栏的用户头像区域 or 设置中
# 先尝试侧边栏
print("Step 1: Open sidebar (tap avatar area)...")
aw.tap(27, 71)  # Top-left avatar/sidebar area
time.sleep(2)

result = aw.ocr_scan_page()
print("\nSidebar elements:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Check if we see "工作状态" or "忙碌" or "在线" etc.
status_kw = ['工作状态', '在线', '忙碌', '离开', '请勿打扰', '隐身', '状态']
found_status = False
for r in result:
    for kw in status_kw:
        if kw in r['text']:
            print(f"\n  *** Found status keyword: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
            found_status = True

if not found_status:
    print("\n  No status keywords found in sidebar. Looking for clickable profile area...")
    # Try clicking on the name/profile area
    # The sidebar usually has the user name near the top
    for r in result:
        if '孟' in r['text'] or '钊' in r['text']:
            print(f"  Found user name: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/sidebar_status.png')
