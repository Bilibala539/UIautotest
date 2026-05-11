"""探索群组批量管理功能"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# Start POPO
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(5)

# Navigate to 通讯录 → 群组
print("Step 1: Go to contacts groups...")
aw.click_text("通讯录", timeout=10)
time.sleep(1)
aw.click_text("群组", timeout=5)
time.sleep(2)

# Now click "批量管理" button
print("\nStep 2: Click '批量管理'...")
aw.click_text("批量管理", timeout=5)
time.sleep(2)

# OCR scan
result = aw.ocr_scan_page()
print('\n批量管理模式:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for batch operation buttons
batch_kw = ['全选', '退出', '解散', '取消', '完成', '选择', '已选', '勾选', '删除']
print('\n--- Batch operation keywords: ---')
for r in result:
    for kw in batch_kw:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

img = aw.take_screenshot(save_path='explorer_output/screenshots/batch_manage_mode.png')
