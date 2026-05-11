"""探索侧边栏 - 查找设置入口"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Press back to close any popup
print("Step 0: Press back...")
aw.press_back()
time.sleep(1)

# Check if we're on message page
print("Step 1: Go to message page...")
aw.click_text("消息", timeout=5)
time.sleep(1)

# Try clicking the leftmost icon in header - should be user avatar/sidebar
# From the earlier scan, the "消息" title is at x=81-151, y=54-91
# User avatar should be around x=20-50, y=55-88
print("\nStep 2: Click user avatar area at (35, 72)...")
aw.tap(35, 72)
time.sleep(2)

# OCR scan to see if sidebar opened
result = aw.ocr_scan_page()
print('\nAfter clicking avatar area:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Check for sidebar/settings keywords
sidebar_kw = ['设置', '个人', '账号', '退出', '切换', '更多', '分组', '会话', '帮助']
print('\n--- Sidebar/Settings keywords: ---')
for r in result:
    for kw in sidebar_kw:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

# Take screenshot
img = aw.take_screenshot(save_path='explorer_output/screenshots/after_click_avatar.png')
