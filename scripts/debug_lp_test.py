"""Test long press correctly in grp.popoqa93 chat"""
import sys, os, cv2, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.business.mumu import MuMuBusiness
from image.image_name_mapping import *

driver = MuMuDriver(instance_id=0)
aw = MuMuBusiness(driver)

# Force restart POPO
aw.stop_app()
time.sleep(2)
aw.start_app()
time.sleep(5)

# Verify at message list
msg_tab = aw.find_image(MESSAGE_TAB_BLUE, timeout=10)
print(f"Message list: {msg_tab is not None}")

# Send message using send_message method (which opens chat via search)
print("\nSending message to grp.popoqa93...")
msg_text = aw.send_message(recipient="grp.popoqa93", message="hello_fav", isback=False)
print(f"Sent: '{msg_text}', staying in chat")

# Verify we're in the chat page
time.sleep(1)
img = aw.take_screenshot()
cv2.imwrite('screenshots/debug_in_chat.png', img)
items = aw._ocr_raw(img)
print("\nIn chat, OCR:")
for it in items:
    print(f"  '{it['text']}' @ ({it['cx']},{it['cy']})")

# Find message and long press
pos = aw.find_text_by_ocr(msg_text, timeout=5)
print(f"\nMessage '{msg_text}' found at: {pos}")

if pos:
    # Long press with 1.5s (matching the favorite_message method)
    aw.long_press(pos[0], pos[1], duration=1.5)
    time.sleep(1.0)
    
    # Check what appeared
    img2 = aw.take_screenshot()
    cv2.imwrite('screenshots/debug_lp_chat.png', img2)
    items2 = aw._ocr_raw(img2)
    print("\nAfter long press (2s), OCR:")
    for it in items2:
        print(f"  '{it['text']}' @ ({it['cx']},{it['cy']})")
    
    # Check template matching for the menu
    fav_btn = aw.find_image(LONGPRESS_FAVORITE_BUTTON, timeout=2)
    fav_txt = aw.find_image(LONGPRESS_FAVORITE_TEXT, timeout=2)
    print(f"\nTemplate results:")
    print(f"  FAVORITE_BUTTON: {fav_btn}")
    print(f"  FAVORITE_TEXT: {fav_txt}")
    
    # Dismiss
    aw.press_back()
    time.sleep(0.5)

# Back to message list
aw.press_back()
print("\nDone!")
