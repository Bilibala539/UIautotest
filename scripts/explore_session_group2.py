"""探索会话分组 - 将会话添加到分组，验证Tab栏显示"""
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

pos = aw.find_text_by_ocr("浮窗", timeout=3)
if pos:
    aw.click_text("取消", timeout=3)
    time.sleep(1)

# Enter "工作日历" chat settings → "会话分组" → add to "皮皮" group
print("Step 1: Enter '工作日历' chat settings...")
pos = aw.find_text_by_ocr("工作日历", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(3)

aw.tap(270, 70)  # Enter settings
time.sleep(2)

# Find and click "会话分组"
print("Step 2: Click '会话分组'...")
pos = aw.find_text_by_ocr("会话分组", timeout=5)
if not pos:
    aw.swipe_up(distance=200)
    time.sleep(1)
    pos = aw.find_text_by_ocr("会话分组", timeout=5)

if pos:
    aw.tap(pos[0] + 100, pos[1])
    time.sleep(2)
    
    # We should be on "会话分组" page
    # Click the "十" (plus) next to "皮皮" to add current chat to that group
    print("Step 3: Add to '皮皮' group...")
    result = aw.ocr_scan_page()
    for r in result:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    # The "十" (or "+") is at [128, 244], next to "皮皮" at [88, 245]
    # Let's click it
    plus_pos = None
    for r in result:
        if '十' in r['text'] or ('+' in r['text'] and r['cy'] > 200):
            plus_pos = (r['cx'], r['cy'])
            break
    
    if plus_pos:
        print(f"  Clicking '+' at {plus_pos}...")
        aw.tap(plus_pos[0], plus_pos[1])
        time.sleep(2)
    else:
        # Try clicking around where we saw "十" last time
        print("  Clicking at (128, 244) where '十' was before...")
        aw.tap(128, 244)
        time.sleep(2)
    
    # Check the result
    result2 = aw.ocr_scan_page()
    print("\n=== After clicking '+' next to '皮皮' ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/after_add_to_group.png')
    
    # Check if it changed to "x" (remove) or if there's a confirmation
    for r in result2:
        if any(kw in r['text'] for kw in ['已添加', '移除', 'x', '×', '取消', '确认', '成功']):
            print(f"  *** Change detected: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Go back to message list
    print("\n\nStep 4: Return to message list...")
    aw.press_back()
    time.sleep(1)
    aw.press_back()
    time.sleep(1)
    aw.press_back()
    time.sleep(1)
    
    # Check if there's now a "分组Tab" at top
    result3 = aw.ocr_scan_page()
    print("\n=== Message list page (check for Tab) ===")
    print("Top area (y < 150):")
    for r in result3:
        if r['cy'] < 150:
            print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    print("\nAll items:")
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/msg_list_after_group_add.png')
    
    # Look for group tabs
    print("\n--- Looking for group tabs ---")
    for r in result3:
        if any(kw in r['text'] for kw in ['皮皮', '全部', '分组', '更多']):
            print(f"  GROUP TAB: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
else:
    print("  '会话分组' not found")