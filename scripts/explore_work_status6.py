"""探索工作状态 - 详细侧边栏扫描"""
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
print("Step 1: Open sidebar by clicking top-left avatar...")
aw.tap(27, 71)
time.sleep(2)

# OCR scan the sidebar
result = aw.ocr_scan_page()
print("\n=== Sidebar OCR scan results ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] w={r['bbox'][2]-r['bbox'][0]:3d} h={r['bbox'][3]-r['bbox'][1]:3d} \"{r['text']}\"")

# Save sidebar screenshot
aw.take_screenshot(save_path='explorer_output/screenshots/sidebar_full_scan.png')

# Check if "工作状态" is visible in OCR or if there's a status indicator
print("\n=== Looking for work status indicators ===")
status_keywords = ['工作状态', '在线', '忙碌', '离开', '离线', '打扰', '隐身', '状态', '工作', '工作中']
for r in result:
    for kw in status_keywords:
        if kw in r['text']:
            print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}] bbox={r['bbox']}")

# The "工作状态" might be an icon rather than text
# Let's try clicking around the top right area of sidebar
# First check if there's any green/colored dot near the avatar
print("\n\nStep 2: Trying to find work status entry...")
print("Sidebar might have a status icon near avatar area")
print("Let me check around coords (394, 129) area - the bbox there says:")
for r in result:
    if abs(r['cy'] - 129) < 40:
        print(f"  Near y=129: [{r['cx']},{r['cy']}] \"{r['text']}\"")

# It seems the work status might be accessed by clicking on the user's status area
# Let's try clicking on user name area which shows details
# Actually, looking at the OCR output from previous run, clicking (394,129) led to profile page
# That means the "工作状态" coords in the knowledge base is WRONG - it's pointing to profile page

# Let's look for status in profile page instead
print("\n\nStep 3: Going to profile page to check for work status...")
# First close sidebar
aw.press_back()
time.sleep(1)

# Open sidebar again and click user name to go to profile
aw.tap(27, 71)
time.sleep(2)

# Click user name
pos = aw.find_text_by_ocr("孟静娴", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    # Scan profile page
    result2 = aw.ocr_scan_page()
    print("\n=== Profile page OCR scan ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    # Look for work status in profile
    print("\n=== Looking for work status in profile ===")
    for r in result2:
        for kw in status_keywords:
            if kw in r['text']:
                print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    aw.take_screenshot(save_path='explorer_output/screenshots/profile_workstatus_check.png')
    
    # Go back
    aw.press_back()
    time.sleep(1)
else:
    print("  Could not find user name")

# Now let's try another approach - the status might be in settings
print("\n\nStep 4: Checking settings for work status...")
# Open sidebar again
aw.tap(27, 71)
time.sleep(2)
# Click settings
aw.click_text("设置", timeout=5)
time.sleep(2)

result3 = aw.ocr_scan_page()
print("\n=== Settings page OCR scan ===")
for r in result3:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

print("\n=== Looking for work status in settings ===")
for r in result3:
    for kw in ['工作状态', '状态', '在线', '隐私']:
        if kw in r['text']:
            print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/settings_workstatus_check.png')
