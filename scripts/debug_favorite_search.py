"""调试收藏消息和搜索入口失败"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import cv2
import numpy as np
import time
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.business.mumu import MuMuBusiness
from utils.aw.aw_base import AWBase

driver = MuMuDriver(instance_id=0)
aw = MuMuBusiness(driver)

# ===== 1. 测试长按菜单 =====
print("=" * 50)
print("===== 测试长按菜单 =====")
print("=" * 50)

# 先确保在消息列表页
# Force stop and restart POPO
aw.stop_app()
time.sleep(1)
aw._start_popo()
time.sleep(5)

# Check if we're at message list
from image.image_name_mapping import MESSAGE_TAB_BLUE
pos = aw.find_image(MESSAGE_TAB_BLUE, timeout=10)
if pos:
    print(f"✅ 在消息列表页")
else:
    print("❌ 不在消息列表页，尝试登录")
    aw.login('grp.popoqa67@corp.netease.com', 'Lazermlfy1@')
    time.sleep(3)

# Open chat with grp.popoqa93
aw.click_text("grp.popoqa93", timeout=5)
time.sleep(2)

# Find any message to long press
img = aw.take_screenshot()
cv2.imwrite('screenshots/debug_chat_page.png', img)
print(f"Chat page screenshot saved")

# Try to find a message (the previous test sent '2979648223')
msg_pos = aw.find_text_by_ocr('2979648223', timeout=3)
if not msg_pos:
    # Try any message text
    msg_pos = aw.find_text_by_ocr('test_favorite_msg', timeout=3)
if not msg_pos:
    # Send a new message first
    print("No message found, sending one...")
    aw.click_text("在这里输入", timeout=3)
    time.sleep(0.5)
    aw.input_text("fav_test_123")
    aw.press_key("enter")
    time.sleep(1)
    msg_pos = aw.find_text_by_ocr('fav_test_123', timeout=3)

if msg_pos:
    print(f"Message found at: {msg_pos}")
    # Long press
    aw.long_press(msg_pos[0], msg_pos[1], duration=1.5)
    time.sleep(2)
    
    # Screenshot after long press
    img2 = aw.take_screenshot()
    cv2.imwrite('screenshots/debug_longpress_result.png', img2)
    print(f"Long press result saved: {img2.shape}")
    
    # Try to find the long press menu items with OCR
    texts = aw.extract_all_text()
    print(f"All text after long press: {texts}")
    
    # Try image matching for favorite button
    from image.image_name_mapping import LONGPRESS_FAVORITE_BUTTON, LONGPRESS_FAVORITE_TEXT
    fav_btn = aw.find_image(LONGPRESS_FAVORITE_BUTTON, timeout=2)
    fav_txt = aw.find_image(LONGPRESS_FAVORITE_TEXT, timeout=2)
    print(f"LONGPRESS_FAVORITE_BUTTON found: {fav_btn}")
    print(f"LONGPRESS_FAVORITE_TEXT found: {fav_txt}")
    
    # Dismiss menu
    aw.press_back()
    time.sleep(1)
else:
    print("❌ Cannot find any message to long press!")

# Go back to message list
aw.press_back()
time.sleep(1)

# ===== 2. 测试搜索入口 =====
print("\n" + "=" * 50)
print("===== 测试搜索入口 =====")
print("=" * 50)

from image.image_name_mapping import MESSAGE_TAB_SEARCH

# Click search
pos = aw.find_image(MESSAGE_TAB_SEARCH, timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    img3 = aw.take_screenshot()
    cv2.imwrite('screenshots/debug_search_page.png', img3)
    
    # OCR all text
    texts = aw.extract_all_text()
    print(f"Search page text: {texts}")
    
    # Find "日程" position
    rcheng_pos = aw.find_text_by_ocr("日程", timeout=3)
    print(f"日程 position: {rcheng_pos}")
    
    if rcheng_pos:
        # Swipe left from 日程 position with more distance
        print(f"Swiping left from ({rcheng_pos[0]}, {rcheng_pos[1]}) by 300px...")
        aw.swipe(rcheng_pos[0], rcheng_pos[1], rcheng_pos[0] - 300, rcheng_pos[1], duration=0.5)
        time.sleep(1)
        
        img4 = aw.take_screenshot()
        cv2.imwrite('screenshots/debug_search_after_swipe.png', img4)
        
        texts2 = aw.extract_all_text()
        print(f"After swipe text: {texts2}")
        
        # If still no 云空间, try swiping more
        if '云空间' not in str(texts2):
            print("Still no 云空间, swiping more...")
            aw.swipe(400, rcheng_pos[1], 100, rcheng_pos[1], duration=0.5)
            time.sleep(1)
            
            img5 = aw.take_screenshot()
            cv2.imwrite('screenshots/debug_search_after_swipe2.png', img5)
            texts3 = aw.extract_all_text()
            print(f"After 2nd swipe text: {texts3}")

    # Cancel search
    from image.image_name_mapping import SEARCH_CANCEL
    cancel_pos = aw.find_image(SEARCH_CANCEL, timeout=3)
    if cancel_pos:
        aw.tap(cancel_pos[0], cancel_pos[1])
    else:
        aw.press_back()

print("\n===== 调试完成 =====")
