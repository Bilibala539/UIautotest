"""探索设置中的会话分组功能入口"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Go to "更多" tab
print("Step 1: Click '更多' tab...")
aw.click_text("更多", timeout=5)
time.sleep(2)

# OCR scan
result = aw.ocr_scan_page()
print('\n更多 tab page OCR:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Look for settings related keywords
settings_keywords = ['设置', '通用', '消息', '通知', '隐私', '关于', '个人', '分组', '会话']
print('\n--- Settings keywords: ---')
for r in result:
    for kw in settings_keywords:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

# Take screenshot
img = aw.take_screenshot(save_path='explorer_output/screenshots/more_tab_page.png')
