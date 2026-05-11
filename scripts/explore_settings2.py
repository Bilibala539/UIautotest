"""探索设置页面 - 查找会话分组设置"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Click "设置"
print("Step 1: Click '设置'...")
aw.click_text("设置", timeout=5)
time.sleep(2)

# OCR scan settings page
result = aw.ocr_scan_page()
print('\n设置页面 OCR:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

img = aw.take_screenshot(save_path='explorer_output/screenshots/settings_page.png')

# Look for session/group related settings
group_kw = ['分组', '会话', '消息', '列表', '标签', '通知', '隐私', '通用', '聊天']
print('\n--- Relevant settings: ---')
for r in result:
    for kw in group_kw:
        if kw in r['text']:
            print(f'  Found "{kw}" in "{r["text"]}" at [{r["cx"]},{r["cy"]}]')
