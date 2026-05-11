"""探索群组排序功能 - 通讯录→群组"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Start POPO
from utils.devices import get_adb, POPO_PACKAGE
adb = get_adb()
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(5)

# Click 通讯录 tab
print("Step 1: Go to 通讯录...")
aw.click_text("通讯录", timeout=10)
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
    if '群组' in r['text'] or '群' == r['text']:
        print(f"\n  FOUND GROUP: '{r['text']}' at [{r['cx']},{r['cy']}]")

img = aw.take_screenshot(save_path='explorer_output/screenshots/contacts_page.png')
