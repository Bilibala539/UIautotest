"""探索消息列表页分组区域"""
import sys
import os
import logging
import cv2
import numpy as np

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)

from utils.aw import create_aw

aw = create_aw(platform='mumu', instance_id=0)
img = aw.take_screenshot(save_path='explorer_output/screenshots/msg_page_group_explore.png')
print(f'Image shape: {img.shape}')

# 查看y=90到y=250之间是否有分组tab栏
# 先看这个区域的结构
print("\n=== Pixel analysis of group bar region ===")
for y in range(88, 250, 4):
    row = img[y:y+2, :, :]
    avg_brightness = np.mean(row)
    # Check for horizontal divider lines (dark or light)
    min_val = np.min(row[:, 50:490, :].mean(axis=2))
    max_val = np.max(row[:, 50:490, :].mean(axis=2))
    print(f"  y={y:3d}: avg={avg_brightness:.0f}, min={min_val:.0f}, max={max_val:.0f}")

# 查看分组按钮区域 - 在标题"消息"右边是否有≡按钮
# 已知: "消息" text at (116, 72), 搜索按钮在右上角(432, 72), +号在(490, 70)
# 分组更多按钮应该在消息标题下方的tab栏右侧

# 截取y=90-130区域看看是否有tab栏
tab_region = img[90:140, :, :]
cv2.imwrite('explorer_output/screenshots/msg_page_y90_140.png', tab_region)
print("\nSaved y=90-140 region")

# 截取y=140-230区域（置顶头像区域）
pin_region = img[130:230, :, :]
cv2.imwrite('explorer_output/screenshots/msg_page_y130_230.png', pin_region)
print("Saved y=130-230 region (pinned avatars)")

# 看看全页面结构
# OCR scan focused on y=90-140
result = aw.ocr_scan_page(region=(0, 90, 540, 50))
print(f"\nOCR in y=90-140: {result}")

# Also check if there's a tab bar between pinned area and chat list
result2 = aw.ocr_scan_page(region=(0, 220, 540, 40))
print(f"\nOCR in y=220-260: {result2}")
