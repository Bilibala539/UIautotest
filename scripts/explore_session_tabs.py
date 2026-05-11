"""探索会话分组Tab - 检查消息页面顶部区域"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# First click "收起" to collapse back
print("Step 1: Clicking '收起' to collapse...")
aw.click_text("收起", timeout=5)
time.sleep(1)

# Now check the area between header (y=91) and pinned section (y=140)
# This is where session group tabs might be
img = aw.take_screenshot(save_path='explorer_output/screenshots/msg_page_check_tabs.png')

# Check y=91-140 area - between "消息" title and pinned contacts
tab_area = img[91:145, :, :]
cv2.imwrite('explorer_output/screenshots/tab_area_91_145.png', tab_area)
avg = np.mean(tab_area)
print(f'Tab area (y=91-145) avg brightness: {avg:.1f}')

# Check pixel rows to see if there are any text or icons
for y in range(91, 145, 5):
    row = img[y, :, :]
    row_avg = np.mean(row)
    non_white = np.sum(row.mean(axis=1) < 200)
    print(f'  y={y}: avg={row_avg:.1f}, non-white pixels={non_white}')

# Also check the header icons area (right side of "消息" title)
# y=50-91, x=300-540 - there might be + or search icons
header_right = img[50:91, 300:540, :]
cv2.imwrite('explorer_output/screenshots/header_right_icons.png', header_right)
print(f'\nHeader right area (x=300-540, y=50-91):')
non_white = np.sum(header_right.mean(axis=2) < 200)
total = header_right.shape[0] * header_right.shape[1]
print(f'  Non-white pixels: {non_white}/{total} ({100*non_white/total:.1f}%)')

# Look for any icon at specific positions in header
# Typically: search icon, + icon, etc.
for x_start in range(300, 540, 40):
    region = img[55:88, x_start:x_start+40, :]
    nw = np.sum(region.mean(axis=2) < 200)
    if nw > 10:
        print(f'  Icon found at x={x_start}-{x_start+40}, y=55-88: {nw} dark pixels')

# Check if there's a "+" button in the header for adding groups
print("\n--- Searching for + button or session group entry ---")
# Let's look at the specific icon area more carefully
# The "消息" title is at x=81-151, y=54-91
# Icons should be to the right
icon_region = img[50:95, 440:540, :]
cv2.imwrite('explorer_output/screenshots/header_icon_right.png', icon_region)

# Check the full row at y=100-135 - this might be a divider or tab bar
full_row_100_135 = img[100:135, :, :]
cv2.imwrite('explorer_output/screenshots/row_100_135.png', full_row_100_135)
print(f'\nRow y=100-135 avg brightness: {np.mean(full_row_100_135):.1f}')

# OCR scan just the top area (y=50-180)
from utils.aw.search_region import Normal
top_result = aw.ocr_scan_page(region=(0, 50, 540, 130))
print(f'\nTop area OCR (y=50-180):')
for r in top_result:
    print(f'  [{r["cx"]:3d},{r["cy"]:3d}] "{r["text"]}"')
