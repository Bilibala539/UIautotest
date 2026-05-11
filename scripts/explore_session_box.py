"""探索会话盒子 - 查找入口"""
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

print("Step 1: Check message list for 会话盒子...")
result = aw.ocr_scan_page()
print("\n=== Message list page ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Look for 会话盒子 in the message list
print("\n--- Looking for 会话盒子 related items ---")
box_kw = ['会话盒子', '盒子', '收纳', '折叠', '静音', '免打扰']
for r in result:
    for kw in box_kw:
        if kw in r['text']:
            print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

# Try long-pressing on a conversation to see context menu
print("\n\nStep 2: Long press on a conversation...")
# First find a conversation - look for text in the middle area (y > 150, y < 900)
conversations = [r for r in result if 150 < r['cy'] < 850 and r['cx'] < 400]
if conversations:
    target = conversations[0]
    print(f"  Long pressing on \"{target['text']}\" at [{target['cx']},{target['cy']}]")
    # Use adb long press
    adb_path = get_adb()
    x, y = target['cx'], target['cy']
    subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
                   'input', 'swipe', str(x), str(y), str(x), str(y), '1000'], capture_output=True)
    time.sleep(2)
    
    result2 = aw.ocr_scan_page()
    print("\n=== Context menu after long press ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    # Look for "会话盒子" or "添加到" options
    print("\n--- Context menu items: ---")
    menu_kw = ['会话盒子', '盒子', '添加到', '置顶', '取消置顶', '已读', '未读', '删除', '免打扰', '静音', '不显示']
    for r in result2:
        for kw in menu_kw:
            if kw in r['text']:
                print(f"  Menu: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    aw.take_screenshot(save_path='explorer_output/screenshots/conversation_context_menu.png')
    
    # Close menu
    aw.press_back()
    time.sleep(1)

# Try scrolling down in message list to find 会话盒子
print("\n\nStep 3: Scrolling message list to find 会话盒子...")
for i in range(3):
    aw.swipe_up(distance=400)
    time.sleep(1)
    result3 = aw.ocr_scan_page()
    print(f"\n=== After scroll {i+1} ===")
    for r in result3:
        if any(kw in r['text'] for kw in ['会话盒子', '盒子', '收纳']):
            print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    # Print all items
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

aw.take_screenshot(save_path='explorer_output/screenshots/message_list_scrolled.png')

# Now check the "通用设置" for 工作状态自动同步 option
print("\n\nStep 4: Exploring 工作状态自动同步 in General Settings...")
# Go to home first
aw.press_back()
time.sleep(1)
# Navigate: sidebar → settings → general
aw.tap(27, 71)  # sidebar
time.sleep(2)
aw.click_text("设置", timeout=5)
time.sleep(2)
aw.click_text("通用", timeout=5)
time.sleep(2)

# Find and click 工作状态自动同步
pos = aw.find_text_by_ocr("工作状态", timeout=5)
if pos:
    print(f"  Found '工作状态' at {pos}")
    aw.tap(pos[0], pos[1])
    time.sleep(2)
    
    result4 = aw.ocr_scan_page()
    print("\n=== After clicking 工作状态自动同步 ===")
    for r in result4:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/work_status_sync_page.png')
else:
    print("  '工作状态' not found")