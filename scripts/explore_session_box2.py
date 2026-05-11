"""探索会话盒子 - 长按实际会话项"""
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

print("Step 1: Message list page scan...")
result = aw.ocr_scan_page()
aw.take_screenshot(save_path='explorer_output/screenshots/msg_list_for_box.png')

# In the message list, conversations are at y > 230 (below the pinned avatars)
# Let's long press on a conversation around y=375 area ("POPO助手")
# Actually let's try y=480 ("超极长的" group)
print("\nStep 2: Long press on conversation at y~480 area...")
# Use ADB long press at center of a conversation item
x, y = 270, 480  # center of a conversation row
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
               'input', 'swipe', str(x), str(y), str(x), str(y), '1500'], capture_output=True)
time.sleep(2)

result2 = aw.ocr_scan_page()
print("\n=== After long press at (270, 480) ===")
for r in result2:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/longpress_conversation.png')

# Check for context menu items
menu_found = False
for r in result2:
    if any(kw in r['text'] for kw in ['置顶', '取消置顶', '已读', '未读', '删除', '盒子', '免打扰', '不显示', '添加']):
        menu_found = True
        print(f"  MENU ITEM: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

if not menu_found:
    print("\n  No context menu detected. Trying another position...")
    aw.press_back()
    time.sleep(1)
    
    # Try long press at y=375 (POPO助手 area)
    print("\nStep 3: Long press at (270, 375)...")
    subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
                   'input', 'swipe', '270', '375', '270', '375', '1500'], capture_output=True)
    time.sleep(2)
    
    result3 = aw.ocr_scan_page()
    print("\n=== After long press at (270, 375) ===")
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/longpress_conversation2.png')
    
    for r in result3:
        if any(kw in r['text'] for kw in ['置顶', '取消置顶', '已读', '未读', '删除', '盒子', '免打扰', '不显示', '添加到']):
            print(f"  MENU ITEM: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

    # If still no menu, try at y=585 area  
    aw.press_back()
    time.sleep(1)
    
    print("\nStep 4: Long press at (270, 585)...")
    subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
                   'input', 'swipe', '270', '585', '270', '585', '1500'], capture_output=True)
    time.sleep(2)
    
    result4 = aw.ocr_scan_page()
    print("\n=== After long press at (270, 585) ===")
    for r in result4:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/longpress_conversation3.png')
    
    for r in result4:
        if any(kw in r['text'] for kw in ['置顶', '取消置顶', '已读', '未读', '删除', '盒子', '免打扰', '不显示', '添加到', '标为']):
            print(f"  MENU ITEM: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
