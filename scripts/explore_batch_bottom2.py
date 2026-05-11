"""检查选中群组后的底部状态 - v2"""
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

# First check page
result = aw.ocr_scan_page()
print("Current page:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Navigate: if we see "通讯录" in bottom nav
aw.click_text("通讯录", timeout=15)
time.sleep(2)

# Check contacts page
result = aw.ocr_scan_page()
print("\nContacts page elements:")
for r in result:
    if '群' in r['text'] or '组' in r['text'] or '联系' in r['text']:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Try clicking 群组 tab
aw.click_text("群组", timeout=10)
time.sleep(2)

# Verify
result = aw.ocr_scan_page()
for r in result:
    if '批量' in r['text'] or '管理' in r['text']:
        print(f"\n  Found: [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Enter batch manage
aw.click_text("批量管理", timeout=5)
time.sleep(2)

# Select first group
print("\nSelecting first group (tap 54,260)...")
aw.tap(54, 260)
time.sleep(2)

# Check selected count and buttons
result = aw.ocr_scan_page()
print("\nAfter selecting - status:")
for r in result:
    if '已选' in r['text']:
        print(f"  Count: \"{r['text']}\"")
    if r['cy'] > 890:
        print(f"  Bottom [{r['cx']:3d},{r['cy']:3d}]: \"{r['text']}\"")

aw.take_screenshot(save_path='explorer_output/screenshots/batch_selected1_v2.png')
