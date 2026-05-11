"""回到消息页面，尝试第二个header图标和长按操作"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Go back to main screen
print("Going back to message page...")
aw.press_back()  # from 通用
time.sleep(0.5)
aw.press_back()  # from 设置
time.sleep(0.5)
aw.press_back()  # from sidebar
time.sleep(1)

# Make sure we're on message page
aw.click_text("消息", timeout=5)
time.sleep(1)

# Take fresh screenshot
img = aw.take_screenshot(save_path='explorer_output/screenshots/msg_page_fresh2.png')

# The header icons were at x=340-380 (biggest, ~585 pixels) and x=480-520
# Let's try the icon at x=480-500 (which was identified as 183+127 dark pixels)
# This might be a "≡" or filter/view toggle

print("\nStep 1: Click icon at (490, 72) - second rightmost header icon...")
aw.tap(490, 72)
time.sleep(2)

result = aw.ocr_scan_page()
print('\nAfter clicking (490, 72):')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Check if something new appeared
img2 = aw.take_screenshot(save_path='explorer_output/screenshots/after_490_72_click.png')

# If nothing happened, try the icon at (430, 72)
print("\nStep 2: Try icon at (430, 72)...")
aw.tap(430, 72)
time.sleep(2)

result2 = aw.ocr_scan_page()
print('\nAfter clicking (430, 72):')
for r in result2:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    if cy < 400:
        print(f'  [{cx:3d},{cy:3d}] "{text}"')
