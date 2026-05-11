"""探索群组排序 - 关闭弹窗后进入通讯录→群组"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Close the popup
print("Step 0: Close popup by clicking '取消'...")
aw.click_text("取消", timeout=5)
time.sleep(1)

# Navigate to 通讯录
# First we need to find the 通讯录 tab - but it's in the "更多" panel
# From earlier exploration: 通讯录 is at bottom tab (225, 924)
print("\nStep 1: Click 通讯录 tab at bottom...")
aw.tap(225, 924)
time.sleep(2)

# OCR scan
result = aw.ocr_scan_page()
print('\n通讯录页面:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for 群组 entry
for r in result:
    if '群组' in r['text']:
        print(f"\n  FOUND: '{r['text']}' at [{r['cx']},{r['cy']}]")

img = aw.take_screenshot(save_path='explorer_output/screenshots/contacts_page2.png')

# If we see "群组", click on it
group_found = False
for r in result:
    if r['text'] == '群组':
        print(f"\nStep 2: Click '群组' at [{r['cx']},{r['cy']}]...")
        aw.tap(r['cx'], r['cy'])
        group_found = True
        break

if not group_found:
    # Try clicking the text via OCR
    print("\nStep 2: Try click_text '群组'...")
    aw.click_text("群组", timeout=5)

time.sleep(2)

# OCR scan groups page
result2 = aw.ocr_scan_page()
print('\n群组列表页面:')
for r in result2:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for sorting/filter options
sort_kw = ['排序', '筛选', '活跃', '最近', '默认', '管理']
for r in result2:
    for kw in sort_kw:
        if kw in r['text']:
            print(f"  SORT/FILTER: '{r['text']}' at [{r['cx']},{r['cy']}]")

img2 = aw.take_screenshot(save_path='explorer_output/screenshots/groups_list.png')
