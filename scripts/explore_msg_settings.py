"""探索消息设置 - 查找会话分组开关"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Click "消息" in settings
print("Step 1: Click '消息' in settings...")
aw.click_text("消息", timeout=5)
time.sleep(2)

# OCR scan
result = aw.ocr_scan_page()
print('\n消息设置页面 OCR:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

img = aw.take_screenshot(save_path='explorer_output/screenshots/msg_settings_page.png')

# Look for group/session related
group_kw = ['分组', '会话', '标签', '列表', '盒子', '置顶', '未读', '显示']
print('\n--- Group-related settings: ---')
for r in result:
    for kw in group_kw:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

# If page is scrollable, scroll down to check for more options
print("\n--- Scrolling down to check more options... ---")
aw.swipe_up(distance=300)
time.sleep(1)

result2 = aw.ocr_scan_page()
print('\nAfter scrolling down:')
for r in result2:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

for r in result2:
    for kw in group_kw:
        if kw in r['text']:
            print(f'  FOUND: "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')
