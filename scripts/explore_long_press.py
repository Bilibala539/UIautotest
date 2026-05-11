"""尝试长按消息列表项，以及检查是否有隐藏的tab切换"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# We're on message page. Let's try a long press on a conversation item
# "POPO助手" is at (167, 270) - let's long press it
print("Step 1: Long press on 'POPO助手' conversation (167, 270)...")
# Use ADB long press (AWBase might not have a long_press method)
# Actually let's check aw_base for long_press
import subprocess as sp
# Use adb shell input swipe for long press (same point, long duration)
cmd = [adb, '-s', '127.0.0.1:16384', 'shell', 'input', 'swipe', '167', '270', '167', '270', '1000']
sp.run(cmd, capture_output=True)
time.sleep(2)

# OCR scan to see context menu
result = aw.ocr_scan_page()
print('\nAfter long press on conversation:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Check for group/label keywords in context menu
group_kw = ['分组', '标签', '置顶', '删除', '免打扰', '已读', '移动', '标记']
print('\n--- Context menu items: ---')
for r in result:
    for kw in group_kw:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

img = aw.take_screenshot(save_path='explorer_output/screenshots/long_press_conv.png')
