"""探索会话盒子 - 添加会话到盒子并观察"""
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

# Enter a P2P chat (e.g. the "超极长的" group or another conversation)
# Let's use "工作日历" service account since it's a non-critical one
print("Step 1: Open '工作日历' conversation...")
pos = aw.find_text_by_ocr("工作日历", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(3)
else:
    print("  Not found, trying other conversation...")
    aw.tap(270, 290)
    time.sleep(3)

# Go to settings
print("Step 2: Enter chat settings...")
aw.tap(270, 70)  # Click top bar / chat name area
time.sleep(2)

# Scan settings page
result = aw.ocr_scan_page()
print("\n=== Chat settings page ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Find "添加到会话盒子" and click it
print("\n\nStep 3: Click '添加到会话盒子'...")
pos = aw.find_text_by_ocr("添加到会话盒子", timeout=5)
if not pos:
    # Try scrolling down
    aw.swipe_up(distance=200)
    time.sleep(1)
    pos = aw.find_text_by_ocr("添加到会话盒子", timeout=5)

if pos:
    print(f"  Found at {pos}, clicking...")
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    # Check what happened
    result2 = aw.ocr_scan_page()
    print("\n=== After clicking '添加到会话盒子' ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/after_add_to_box.png')
    
    # Check if there's a confirmation dialog or if the option changed
    # If successful, the setting should change to "从会话盒子移出" or similar
    for r in result2:
        if any(kw in r['text'] for kw in ['移出', '已添加', '从会话盒子', '确认', '取消']):
            print(f"  *** STATE CHANGE: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Go back to message list
    print("\n\nStep 4: Going back to message list...")
    aw.press_back()
    time.sleep(1)
    aw.press_back()
    time.sleep(1)
    
    # Scan message list for 会话盒子
    result3 = aw.ocr_scan_page()
    print("\n=== Message list after adding to 会话盒子 ===")
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/msg_list_with_box.png')
    
    # Look for 会话盒子 entry
    print("\n--- Looking for 会话盒子 in message list ---")
    for r in result3:
        if any(kw in r['text'] for kw in ['会话盒子', '盒子', '收纳']):
            print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Scroll down in message list to see if 会话盒子 appears at bottom
    print("\n\nStep 5: Scrolling message list to find 会话盒子...")
    for i in range(3):
        aw.swipe_up(distance=300)
        time.sleep(1)
        result_scroll = aw.ocr_scan_page()
        for r in result_scroll:
            if any(kw in r['text'] for kw in ['会话盒子', '盒子', '收纳']):
                print(f"  FOUND after scroll {i+1}: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
        # Print conversation items
        for r in result_scroll:
            if 100 < r['cy'] < 900:
                print(f"  scroll{i+1}: [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
else:
    print("  '添加到会话盒子' not found in settings page")
    # Take screenshot to debug
    aw.take_screenshot(save_path='explorer_output/screenshots/settings_no_box_option.png')
