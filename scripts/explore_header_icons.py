"""探索消息页面header右侧图标"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Take initial screenshot to identify icon positions precisely
img = aw.take_screenshot(save_path='explorer_output/screenshots/msg_page_icons.png')

# Focus on header right area: y=50-91, x=300-540
# Let's analyze each icon region more precisely
print("Analyzing header icons...")
for x_start in range(300, 540, 20):
    region = img[55:88, x_start:x_start+20, :]
    nw = np.sum(region.mean(axis=2) < 180)
    if nw > 5:
        print(f'  Dark content at x={x_start}-{x_start+20}: {nw} pixels')

# Save detailed icon crops
# Icon 1 area: x=330-380 (biggest cluster)
icon1 = img[50:95, 330:385, :]
cv2.imwrite('explorer_output/screenshots/icon1_330_385.png', icon1)

# Icon 2 area: x=410-460
icon2 = img[50:95, 410:465, :]
cv2.imwrite('explorer_output/screenshots/icon2_410_465.png', icon2)

# Icon 3 area: x=460-510
icon3 = img[50:95, 460:515, :]
cv2.imwrite('explorer_output/screenshots/icon3_460_515.png', icon3)

# Icon 4 area: x=500-540
icon4 = img[50:95, 500:540, :]
cv2.imwrite('explorer_output/screenshots/icon4_500_540.png', icon4)

# Try clicking the + button (likely at x=500-520, y=65-75)
# First let's try clicking the rightmost icon
print("\nStep 1: Clicking at (510, 72) - rightmost header icon area...")
aw.tap(510, 72)
time.sleep(2)

# OCR scan after click
img2 = aw.take_screenshot(save_path='explorer_output/screenshots/after_click_right_icon.png')
result = aw.ocr_scan_page()
print('\nAfter clicking right icon - OCR:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Check if a menu appeared
menu_keywords = ['创建', '扫一扫', '加好友', '面对面', '群聊', '分组', '新消息']
print('\n--- Menu items found: ---')
for r in result:
    for kw in menu_keywords:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')
