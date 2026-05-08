"""Quick check current state"""
import sys, os, cv2, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.aw_base import AWBase

from utils.aw.business.mumu import MuMuBusiness

driver = MuMuDriver(instance_id=0)
aw = MuMuBusiness(driver)

# Start POPO first
aw.start_app()
time.sleep(5)
from image.image_name_mapping import MESSAGE_TAB_BLUE
msg_tab = aw.find_image(MESSAGE_TAB_BLUE, timeout=15)
if msg_tab:
    print("POPO is at message list page")
else:
    print("Not at message list, trying login...")
    aw.login('grp.popoqa67@corp.netease.com', 'Lazermlfy1@')
    time.sleep(3)

# Take screenshot and OCR
img = aw.take_screenshot()
cv2.imwrite('screenshots/state_now.png', img)
items = aw._ocr_raw(img)
print("Current page OCR:")
for it in items:
    print(f"  '{it['text']}' @ ({it['cx']},{it['cy']})")

# Now test: long press on any message, check what happens
# First, navigate to grp.popoqa93 chat
pos = aw.find_text_by_ocr("grp.popoqa93", timeout=3)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    # Find a message to long press
    img2 = aw.take_screenshot()
    items2 = aw._ocr_raw(img2)
    print("\nChat page OCR:")
    for it in items2:
        print(f"  '{it['text']}' @ ({it['cx']},{it['cy']})")
    
    # Long press the last visible message (bottom-most text that's not input area)
    # Find '2979648223' or any message
    target = None
    for it in items2:
        if '2979648223' in it['text'] or 'fav_test' in it['text']:
            target = it
            break
    
    if not target:
        # Just use the first non-system text in the chat
        for it in reversed(items2):
            if it['cy'] > 100 and it['cy'] < 800 and it['cx'] > 50:
                target = it
                break
    
    if target:
        print(f"\nLong pressing: '{target['text']}' @ ({target['cx']},{target['cy']})")
        aw.long_press(target['cx'], target['cy'], duration=1.5)
        time.sleep(2)
        
        img3 = aw.take_screenshot()
        cv2.imwrite('screenshots/debug_longpress_actual.png', img3)
        items3 = aw._ocr_raw(img3)
        print("\nAfter long press OCR:")
        for it in items3:
            print(f"  '{it['text']}' @ ({it['cx']},{it['cy']})")
        
        # Try template match
        from image.image_name_mapping import LONGPRESS_FAVORITE_BUTTON, LONGPRESS_FAVORITE_TEXT
        fav_btn = aw.find_image(LONGPRESS_FAVORITE_BUTTON, timeout=2)
        fav_txt = aw.find_image(LONGPRESS_FAVORITE_TEXT, timeout=2)
        print(f"\nLONGPRESS_FAVORITE_BUTTON match: {fav_btn}")
        print(f"LONGPRESS_FAVORITE_TEXT match: {fav_txt}")
        
        # Dismiss
        aw.press_back()
    else:
        print("No target message found!")
    
    aw.press_back()
else:
    print("grp.popoqa93 not found on current page!")
