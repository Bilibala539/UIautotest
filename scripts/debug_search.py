"""Test search tabs"""
import sys, os, cv2, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.business.mumu import MuMuBusiness

driver = MuMuDriver(instance_id=0)
aw = MuMuBusiness(driver)

from image.image_name_mapping import MESSAGE_TAB_SEARCH

# Click search button
pos = aw.find_image(MESSAGE_TAB_SEARCH, timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    img = aw.take_screenshot()
    cv2.imwrite('screenshots/debug_search_tabs.png', img)
    items = aw._ocr_raw(img)
    print("Search page OCR:")
    for it in items:
        print(f"  '{it['text']}' @ ({it['cx']},{it['cy']})")
    
    # Find 日程 and swipe left
    rcheng_pos = aw.find_text_by_ocr("日程", timeout=3)
    if rcheng_pos:
        print(f"\n日程 at: {rcheng_pos}")
        # Multiple swipe attempts
        for attempt in range(3):
            aw.swipe(rcheng_pos[0], rcheng_pos[1], rcheng_pos[0] - 200, rcheng_pos[1], duration=0.5)
            time.sleep(1)
            img2 = aw.take_screenshot()
            items2 = aw._ocr_raw(img2)
            texts = [it['text'] for it in items2]
            print(f"  Swipe {attempt+1}: {texts}")
            if any('云空间' in t for t in texts):
                print(f"  Found 云空间!")
                break
    
    # Cancel search
    aw.press_back()
else:
    print("Search button not found!")
