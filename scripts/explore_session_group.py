"""探索会话分组 - 从设置页面的'会话分组'入口"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb_path = get_adb()

# Force stop and restart
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 'am', 'force-stop', POPO_PACKAGE], capture_output=True)
time.sleep(2)
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(10)

# Handle permission popup
pos = aw.find_text_by_ocr("浮窗", timeout=3)
if pos:
    aw.click_text("取消", timeout=3)
    time.sleep(1)

# Enter a group chat settings to find "会话分组"
# Use "工作日历" which we already know has "会话分组" option
print("Step 1: Enter '工作日历' chat...")
pos = aw.find_text_by_ocr("工作日历", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(3)

# Go to settings
print("Step 2: Enter chat settings...")
aw.tap(270, 70)
time.sleep(2)

# Look for 会话分组 and click it
print("Step 3: Looking for '会话分组'...")
pos = aw.find_text_by_ocr("会话分组", timeout=5)
if not pos:
    aw.swipe_up(distance=200)
    time.sleep(1)
    pos = aw.find_text_by_ocr("会话分组", timeout=5)

if pos:
    print(f"  Found '会话分组' at {pos}")
    # Click on "选择分组>" or the whole row
    aw.tap(pos[0] + 100, pos[1])  # Click slightly to the right to hit "选择分组>"
    time.sleep(2)
    
    result = aw.ocr_scan_page()
    print("\n=== 会话分组 page ===")
    for r in result:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/session_group_page.png')
    
    # Explore this page
    print("\n--- Looking for group management options ---")
    for r in result:
        if any(kw in r['text'] for kw in ['分组', '新增', '管理', '添加', '未命名', '全部', '默认']):
            print(f"  Option: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Check if there's a right-top button for management
    # Check for "+" or "设置" or gear icon at top right
    for r in result:
        if r['cy'] < 100 and r['cx'] > 400:
            print(f"  Top-right: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # If there are group options, try clicking one
    # Also look for "管理" button
    manage_pos = aw.find_text_by_ocr("管理", timeout=3)
    if manage_pos:
        print(f"\n  Found '管理' at {manage_pos}")
    
    # Also check for "添加" button at top right
    add_pos = aw.find_text_by_ocr("添加", timeout=3)
    if add_pos:
        print(f"  Found '添加' at {add_pos}")
    
    # Let's also check the "选择分组>" text again - it might be the actual button
    aw.press_back()
    time.sleep(1)
else:
    print("  '会话分组' not found")

# Now let's go back and check the message list page for 分组Tab
print("\n\nStep 4: Back to message list to check for 分组 Tab...")
aw.press_back()
time.sleep(1)
aw.press_back()
time.sleep(1)

# Look carefully at the top area of message list for tabs
result2 = aw.ocr_scan_page()
print("\n=== Message list top area (y < 150) ===")
for r in result2:
    if r['cy'] < 150:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/msg_list_top_for_tabs.png')

# Check if there's a "≡" or hamburger menu near the message tab
# This could be the "分组面板" trigger
print("\n--- Looking for 分组/tab indicators ---")
for r in result2:
    if any(kw in r['text'] for kw in ['分组', '全部', '≡', '三', '目']):
        print(f"  Tab indicator: \"{r['text']}\" at [{r['cx']},{r['cy']}]")