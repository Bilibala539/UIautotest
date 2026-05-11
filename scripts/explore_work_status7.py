"""探索工作状态 - 点击'工卡'位置"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# Force stop and restart
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'am', 'force-stop', POPO_PACKAGE], capture_output=True)
time.sleep(2)
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(10)

# Handle permission popup
pos = aw.find_text_by_ocr("浮窗", timeout=3)
if pos:
    aw.click_text("取消", timeout=3)
    time.sleep(1)

# Open sidebar
print("Step 1: Open sidebar...")
aw.tap(27, 71)
time.sleep(2)

# The OCR saw "工卡" at [389, 206], which is likely a work status card/badge
# Let's click it
print("Step 2: Click '工卡' area at (389, 206)...")
aw.tap(389, 206)
time.sleep(3)

# OCR scan what happened
result = aw.ocr_scan_page()
print("\n=== After clicking '工卡' area ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

aw.take_screenshot(save_path='explorer_output/screenshots/work_status_after_workcard.png')

# Look for status options
print("\n--- Status keywords: ---")
status_kw = ['工作状态', '在线', '忙碌', '离开', '请勿打扰', '隐身', '状态', '会议中', 
             '休息', '外出', '出差', '设置', '清除', '工卡', '卡片', '自定义']
for r in result:
    for kw in status_kw:
        if kw in r['text']:
            print(f"  Found: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

# If we see profile page (个性签名, 中文昵称 etc), it means it's the profile page
# Let's check if there's a "工作状态" section in the profile
has_profile_markers = any('个性签名' in r['text'] or '中文昵称' in r['text'] for r in result)
if has_profile_markers:
    print("\n\n  ** Entered profile page - scrolling down to find work status **")
    aw.swipe_up(distance=400)
    time.sleep(2)
    result2 = aw.ocr_scan_page()
    print("\n=== Profile page after scroll ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    aw.take_screenshot(save_path='explorer_output/screenshots/profile_scroll_workstatus.png')
    
    # Scroll more
    aw.swipe_up(distance=400)
    time.sleep(2)
    result3 = aw.ocr_scan_page()
    print("\n=== Profile page after 2nd scroll ===")
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    aw.take_screenshot(save_path='explorer_output/screenshots/profile_scroll2_workstatus.png')
    
    # Go back
    aw.press_back()
    time.sleep(1)
    
    # Try accessing work status from message page directly
    # Some apps have status in the header bar
    print("\n\nStep 3: Back to message page, checking for status icon in header...")
    # Handle any popups
    pos = aw.find_text_by_ocr("浮窗", timeout=2)
    if pos:
        aw.click_text("取消", timeout=2)
        time.sleep(1)
    
    result4 = aw.ocr_scan_page()
    print("\n=== Current page ===")
    for r in result4:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/after_profile_back.png')
