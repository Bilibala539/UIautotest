"""检查选中群组后的底部状态"""
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
time.sleep(8)

# Navigate
aw.click_text("通讯录", timeout=15)
time.sleep(1)
aw.click_text("群组", timeout=5)
time.sleep(2)
aw.click_text("批量管理", timeout=5)
time.sleep(2)

# Select first group
aw.tap(54, 260)
time.sleep(2)

# Full OCR of bottom area
result = aw.ocr_scan_page()
print("After selecting 1 group - ALL bottom area elements (y > 850):")
for r in result:
    if r['cy'] > 850:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

print("\nAll elements with '退出' or '解散' or '群组':")
for r in result:
    if any(kw in r['text'] for kw in ['退出', '解散', '群组', '全选']):
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

print("\nFull bottom region (y > 880):")
for r in result:
    if r['cy'] > 880:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] bbox={r.get('bbox')} \"{r['text']}\"")

# Screenshot
img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_selected1_bottom.png')
print(f"\nScreenshot saved")
