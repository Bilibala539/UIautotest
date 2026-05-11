"""探索工作状态 - 在侧边栏头像区域寻找状态入口"""
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

# In the sidebar OCR output, we saw:
# [82,204] "孟静娴" (username)
# [389,206] "工卡" (possibly work card icon area - but clicking it opened a contact)
# Let's try clicking more precisely on the user avatar area to look for status
# The avatar is probably on the left side around x=60-80, y=120-160

# Let me try clicking on the area BELOW the username, around y=280-330
# That's where "个性签名" info shows in sidebar
# Actually, let's check if there's a status indicator by the avatar

# First, let me check "帮助与反馈" section - maybe sidebar has changed
# Let's scan more carefully and look for the sidebar avatar area

# In POPO, the work status might be:
# 1. A small colored dot next to the avatar
# 2. A text below/beside the username like "在线"/"忙碌"  
# 3. An entry in settings → privacy/general

# Let's check settings > privacy
print("Step 2: Going to Settings...")
aw.click_text("设置", timeout=5)
time.sleep(2)

result = aw.ocr_scan_page()
print("\n=== Settings page ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/settings_for_workstatus.png')

# Check privacy settings
print("\n\nStep 3: Entering Privacy settings...")
pos = aw.find_text_by_ocr("隐私", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    result2 = aw.ocr_scan_page()
    print("\n=== Privacy settings ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/privacy_settings.png')
    
    # Look for work status in privacy
    for r in result2:
        if any(kw in r['text'] for kw in ['工作状态', '状态', '在线', '显示']):
            print(f"  *** FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Scroll down to see more
    aw.swipe_up(distance=300)
    time.sleep(1)
    result3 = aw.ocr_scan_page()
    print("\n=== Privacy settings after scroll ===")
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    aw.press_back()
    time.sleep(1)
else:
    print("  Not found '隐私'")

# Check general settings
print("\n\nStep 4: Entering General settings...")
pos = aw.find_text_by_ocr("通用", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    result4 = aw.ocr_scan_page()
    print("\n=== General settings ===")
    for r in result4:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/general_settings.png')
    
    # Look for work status
    for r in result4:
        if any(kw in r['text'] for kw in ['工作状态', '状态', '在线']):
            print(f"  *** FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    aw.press_back()
    time.sleep(1)
else:
    print("  Not found '通用'")

# Let's also try opening profile and scrolling all the way
print("\n\nStep 5: Full profile page exploration...")
aw.press_back()
time.sleep(1)
# Now on sidebar or message page
aw.tap(27, 71)  # Open sidebar
time.sleep(2)

# Click on avatar/username to enter profile
pos = aw.find_text_by_ocr("孟静娴", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    # Scan and scroll through entire profile
    for i in range(5):
        result_p = aw.ocr_scan_page()
        print(f"\n=== Profile page scroll {i} ===")
        for r in result_p:
            print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
        
        # Check for work status
        for r in result_p:
            if any(kw in r['text'] for kw in ['工作状态', '状态设置', '在线状态', '工作中', '忙碌']):
                print(f"  *** FOUND WORK STATUS: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
        
        aw.swipe_up(distance=300)
        time.sleep(1)
    
    aw.take_screenshot(save_path='explorer_output/screenshots/profile_bottom.png')
