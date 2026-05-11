"""探索侧边栏并生成AW - Row 71: 打开个人中心-有侧边栏"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Go back to top of message list
print("Going back to message page top...")
aw.swipe_down(distance=600)
time.sleep(1)
aw.swipe_down(distance=600)
time.sleep(1)

# Verify on message page
result = aw.ocr_scan_page()
on_msg = any('消息' in r['text'] for r in result if r['cy'] < 100)
print(f"On message page: {on_msg}")

# Open sidebar
print("\nStep 1: Open sidebar (click avatar at 35, 72)...")
aw.tap(35, 72)
time.sleep(2)

# Scan sidebar content
result = aw.ocr_scan_page()
print("\nSidebar content:")
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    bbox = r['bbox']
    print(f'  [{cx:3d},{cy:3d}] bbox={bbox} "{text}"')

img = aw.take_screenshot(save_path='explorer_output/screenshots/sidebar_full.png')

# Verify expected items from Row 71:
# "服务按照以下顺序排列：徽章-我的收藏-签包-帮助与反馈-登录设备管理-设置"
expected_items = ['徽章', '我的收藏', '签包', '帮助与反馈', '登录设备管理', '设置']
found_items = []
for item in expected_items:
    for r in result:
        if item in r['text']:
            found_items.append(item)
            break

print(f"\nExpected items found: {found_items}")
print(f"Missing items: {[i for i in expected_items if i not in found_items]}")

# Also check for 工卡 (Row 72 mentions 电子工卡)
for r in result:
    if '工卡' in r['text']:
        print(f"\n  Found 工卡: '{r['text']}' at [{r['cx']},{r['cy']}]")
