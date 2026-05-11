"""探索批量管理 - 重新导航并测试checkbox"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# Force stop and restart POPO
subprocess.run([get_adb(), '-s', '127.0.0.1:16384', 'shell', 'am', 'force-stop', POPO_PACKAGE], capture_output=True)
time.sleep(2)
subprocess.run([get_adb(), '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(8)

# Check current page
result = aw.ocr_scan_page()
print("Current page elements:")
for r in result:
    if r['cy'] > 860:  # Bottom nav area
        print(f"  Bottom: [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Click 通讯录 tab
print("\nStep 1: Click 通讯录...")
aw.click_text("通讯录", timeout=15)
time.sleep(2)

# Click 群组
print("Step 2: Click 群组...")
aw.click_text("群组", timeout=5)
time.sleep(2)

# Click 批量管理
print("Step 3: Click 批量管理...")
aw.click_text("批量管理", timeout=5)
time.sleep(2)

# Screenshot the batch management mode
img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_v2.png')
print(f"Screenshot saved: {img.shape}")

# Full OCR to get accurate positions
result = aw.ocr_scan_page()
print("\nFull OCR in batch mode:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] bbox={r.get('bbox', 'N/A')} \"{r['text']}\"")

# Now the right side icons that look like "口" are actually checkboxes
# They appear as letters in the alphabetical index on the RIGHT edge
# The actual checkboxes might be AT the beginning of each row (left side)
# Let's look at the image more carefully - the items like 口/E/F/K etc at x=522
# are the ALPHABET INDEX on the right edge, NOT checkboxes!
# The actual checkbox is likely an icon (not text) that OCR can't read

# Let's try clicking closer to the group items (left of group name)
# Group icons/avatars are at x≈54, then group names at x≈200+
# Checkboxes in batch mode usually appear as circles before the avatar

print("\n\nStep 4: Try selecting by clicking left side of row...")
# First group "aaaaa7" is at y≈248-278 area  
# Try left edge where a checkbox would appear
aw.tap(22, 260)  # Far left
time.sleep(1.5)

result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        print(f"After tap (22,260): {r['text']}")
        break
else:
    print("After tap (22,260): No change")

# Try at the avatar position
aw.tap(54, 260)
time.sleep(1.5)

result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        print(f"After tap (54,260): {r['text']}")
        break

# Try at the group name area
aw.tap(200, 260)
time.sleep(1.5)

result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        print(f"After tap (200,260): {r['text']}")
        break

# Try tapping the whole row more precisely - the second group at a known y
# "aefbv (0)" is at y≈407, let's try that row
print("\nStep 5: Try second group row...")
aw.tap(270, 420)  # Middle of second group row
time.sleep(1.5)

result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        print(f"After tap (270,420): {r['text']}")
        break

# The issue might be that after "全选" changed the sort order
# Let's just tap the row more aggressively
aw.tap(300, 300)
time.sleep(1.5)

result = aw.ocr_scan_page()
for r in result:
    if "已选" in r['text']:
        print(f"After tap (300,300): {r['text']}")
        break

img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_click_test.png')
print("\nFinal screenshot saved.")
