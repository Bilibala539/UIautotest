"""探索批量管理 - 精确定位checkbox并测试勾选"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# Start POPO
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(5)

# Navigate to 通讯录 → 群组 → 批量管理
print("Navigate to batch manage mode...")
aw.click_text("通讯录", timeout=10)
time.sleep(1)
aw.click_text("群组", timeout=5)
time.sleep(2)
aw.click_text("批量管理", timeout=5)
time.sleep(2)

# Take screenshot for analysis
img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_fresh.png')
print(f"Screenshot saved. Shape: {img.shape}")

# Let's try clicking on the group item itself (not just the checkbox icon)
# From OCR, first group "aaaaa7..." center around x=209, y=278
# The checkbox "口" was detected at x=522, y=258
# Let's try tapping at different x positions to find the clickable checkbox
print("\nTrying to select by tapping the group row at different positions...")

# Try tapping the full row width near the first group
# The "口" text is at y=258, let's tap exactly there with x=510 (slightly left of detected)
aw.tap(510, 260)
time.sleep(1.5)

# OCR scan
result = aw.ocr_scan_page()
selected_count = "unknown"
for r in result:
    if "已选" in r['text']:
        selected_count = r['text']
        break
print(f"After tap (510,260): {selected_count}")

# If still 0, try tapping the group row itself (middle of row)
if "0" in selected_count:
    aw.tap(270, 260)
    time.sleep(1.5)
    result = aw.ocr_scan_page()
    for r in result:
        if "已选" in r['text']:
            selected_count = r['text']
            break
    print(f"After tap (270,260): {selected_count}")

# If still 0, try tapping with the full scan to detect exact checkbox coords
if "0" in selected_count:
    # Maybe we need to scroll down first since the "sort" dropdown changed the view
    # Let's try tapping at y=250 (slightly above)
    aw.tap(510, 250)
    time.sleep(1.5)
    result = aw.ocr_scan_page()
    for r in result:
        if "已选" in r['text']:
            selected_count = r['text']
            break
    print(f"After tap (510,250): {selected_count}")

# Let's try with the actual image and detect checkbox visually
img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_attempt.png')

# Try clicking more to the right
aw.tap(520, 265)
time.sleep(1.5)
result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        selected_count = r['text']
        break
print(f"After tap (520,265): {selected_count}")

# Try far right
aw.tap(505, 270)
time.sleep(1.5)
result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        selected_count = r['text']
        break
print(f"After tap (505,270): {selected_count}")

# Screenshot final state
img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_final.png')
print("\nDone. Check screenshots for visual analysis.")
