"""通过群聊设置找到会话分组入口"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# First go back to message page
print("Step 0: Press back to message page...")
aw.press_back()
time.sleep(1)

# Click on the "消息" tab to ensure we're there
aw.click_text("消息", timeout=5)
time.sleep(1)

# Click on a group chat - "超极长的" seems like a group
print("\nStep 1: Click on a group chat '超极长的'...")
aw.click_text("超极长的", timeout=5)
time.sleep(2)

# Now we're in a chat - click group name at top to enter settings
result = aw.ocr_scan_page()
print('\nIn chat page:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    if cy < 100:
        print(f'  [{cx:3d},{cy:3d}] "{text}"')

# The group name should be at top center - click it
# Group settings usually accessed by clicking title area
print("\nStep 2: Click on group name at top (270, 40)...")
aw.tap(270, 40)
time.sleep(2)

# Check if we're in group settings
result2 = aw.ocr_scan_page()
print('\nAfter clicking group title:')
for r in result2:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for 会话分组 entry
for r in result2:
    if '会话分组' in r['text'] or '分组' in r['text']:
        print(f'\n  FOUND: "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

img = aw.take_screenshot(save_path='explorer_output/screenshots/group_settings_page.png')
