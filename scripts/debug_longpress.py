"""Test long press menu for favorite"""
import sys, os, cv2, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.business.mumu import MuMuBusiness
from image.image_name_mapping import *

driver = MuMuDriver(instance_id=0)
aw = MuMuBusiness(driver)

# Ensure at message list page first
aw.press_back()
time.sleep(0.5)
aw.press_back()
time.sleep(0.5)
aw.press_back()
time.sleep(1)
msg_tab = aw.find_image(MESSAGE_TAB_BLUE, timeout=5)
if not msg_tab:
    aw.stop_app()
    time.sleep(1)
    aw.start_app()
    time.sleep(5)

# Send message and stay in chat (isback=False)
print("Sending message...")
msg_text = aw.send_message(recipient="grp.popoqa93", message="favtest999", isback=False)
print(f"Message sent: '{msg_text}'")
time.sleep(1)

# Now long press on the message
print(f"Finding message text to long press...")
pos = aw.find_text_by_ocr(msg_text, timeout=5)
if pos:
    print(f"  Found at: {pos}")
    print(f"  Long pressing...")
    aw.long_press(pos[0], pos[1], duration=1.5)
    time.sleep(2)
    
    # Take screenshot
    img = aw.take_screenshot()
    cv2.imwrite('screenshots/debug_longpress_menu.png', img)
    print(f"  Screenshot saved: {img.shape}")
    
    # OCR
    items = aw._ocr_raw(img)
    print(f"  OCR after long press:")
    for it in items:
        print(f"    '{it['text']}' @ ({it['cx']},{it['cy']})")
    
    # Template matching
    print(f"\n  Template matching:")
    fav_btn = aw.find_image(LONGPRESS_FAVORITE_BUTTON, timeout=2)
    print(f"    LONGPRESS_FAVORITE_BUTTON: {fav_btn}")
    fav_txt = aw.find_image(LONGPRESS_FAVORITE_TEXT, timeout=2)
    print(f"    LONGPRESS_FAVORITE_TEXT: {fav_txt}")
    
    # Press back to dismiss
    aw.press_back()
else:
    print("  Message not found!")
    img = aw.take_screenshot()
    cv2.imwrite('screenshots/debug_msg_not_found.png', img)
    items = aw._ocr_raw(img)
    print("  Current page OCR:")
    for it in items:
        print(f"    '{it['text']}' @ ({it['cx']},{it['cy']})")

# Go back
aw.press_back()
print("\nDone!")
