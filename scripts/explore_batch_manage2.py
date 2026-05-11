"""探索群组批量管理 - 选择群组后的状态"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# We are already in 批量管理 mode from previous script
# Try to select a group by tapping the checkbox on the right (x=522)
# Let's tap the first group's checkbox area

print("Step 1: Select first group (aaaaa7 群)...")
aw.tap(522, 258)  # First group checkbox
time.sleep(2)

# OCR scan to see status change
result = aw.ocr_scan_page()
print('\n选中1个群后:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    if any(kw in text for kw in ['全选', '退出', '解散', '取消', '已选', '选']):
        print(f'  [{cx:3d},{cy:3d}] "{text}"')

img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_selected1.png')

# Now check if "退出群组" and "解散群组" are clickable/enabled
# Try to select another group (non-owner)
print("\nStep 2: Select another group (aefbv)...")
aw.tap(522, 433)  # Second group checkbox
time.sleep(2)

result = aw.ocr_scan_page()
print('\n选中2个群后:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    if any(kw in text for kw in ['全选', '退出', '解散', '取消', '已选', '选']):
        print(f'  [{cx:3d},{cy:3d}] "{text}"')

img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_selected2.png')

# Deselect all and try "全选"
print("\nStep 3: Deselect both and try 全选...")
aw.tap(522, 258)  # Deselect first
time.sleep(1)
aw.tap(522, 433)  # Deselect second
time.sleep(1)

# Now tap 全选
aw.tap(60, 914)  # 全选 button
time.sleep(2)

result = aw.ocr_scan_page()
print('\n全选后:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    if any(kw in text for kw in ['全选', '退出', '解散', '取消', '已选', '选']):
        print(f'  [{cx:3d},{cy:3d}] "{text}"')

img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_selectall.png')

# Cancel the batch management mode
print("\nStep 4: Cancel batch management...")
aw.click_text("取消", timeout=5)
time.sleep(2)

result = aw.ocr_scan_page()
print('\n取消后:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')
