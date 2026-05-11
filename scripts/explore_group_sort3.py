"""探索群组排序选项"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# We're on groups page. Click the sort icon (三 at 47, 139) or "群组名称"
print("Step 1: Click sort area (三 at 47, 139)...")
aw.tap(47, 139)
time.sleep(2)

# OCR scan
result = aw.ocr_scan_page()
print('\nAfter clicking sort icon:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for sort options
sort_kw = ['名称', '活跃', '近', '远', '创建', '排序', '默认', '升序', '降序']
print('\n--- Sort options: ---')
for r in result:
    for kw in sort_kw:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

img = aw.take_screenshot(save_path='explorer_output/screenshots/group_sort_options.png')
