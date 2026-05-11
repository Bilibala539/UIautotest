"""继续滚动消息设置页面 + 检查通用设置"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)

# Continue scrolling down
print("Scrolling down more in message settings...")
aw.swipe_up(distance=400)
time.sleep(1)

result = aw.ocr_scan_page()
print('\nAfter more scroll:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Scroll once more
aw.swipe_up(distance=400)
time.sleep(1)

result2 = aw.ocr_scan_page()
print('\nAfter even more scroll:')
for r in result2:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

# Check for group keywords
group_kw = ['分组', '会话分组', '会话标签', '会话盒子', '标签栏']
for r in result2:
    for kw in group_kw:
        if kw in r['text']:
            print(f'  FOUND GROUP SETTING: "{r["text"]}" at [{r["cx"]},{r["cy"]}]')

# If nothing found, go back and try "通用" setting
print("\n--- Going back to try 通用 setting ---")
aw.press_back()
time.sleep(1)

# Now in settings main page, click "通用"
aw.click_text("通用", timeout=5)
time.sleep(2)

result3 = aw.ocr_scan_page()
print('\n通用设置页面 OCR:')
for r in result3:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    print(f'  [{cx:3d},{cy:3d}] "{text}"')

for r in result3:
    for kw in ['分组', '会话', '标签', '列表', '盒子']:
        if kw in r['text']:
            print(f'  FOUND: "{r["text"]}" at [{r["cx"]},{r["cy"]}]')
