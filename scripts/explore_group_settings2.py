"""进入群设置 - 点击群名或成员数"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# We're in the chat. Try clicking "437名群成员" to enter group settings
print("Step 1: Click '437名群成员' (269, 86)...")
aw.tap(269, 86)
time.sleep(2)

# OCR scan
result = aw.ocr_scan_page()
print('\nAfter clicking group member count:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for 会话分组 
for r in result:
    if '分组' in r['text'] or '置顶' in r['text'] or '盒子' in r['text'] or '标签' in r['text']:
        print(f'\n  RELEVANT: "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

img = aw.take_screenshot(save_path='explorer_output/screenshots/group_settings2.png')

# If we're in group settings, scroll down to find 会话分组
print("\n--- Scrolling to find 会话分组 ---")
aw.swipe_up(distance=300)
time.sleep(1)

result2 = aw.ocr_scan_page()
print('\nAfter scroll:')
for r in result2:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')
    if '分组' in text or '盒子' in text:
        print(f'    *** FOUND ***')
