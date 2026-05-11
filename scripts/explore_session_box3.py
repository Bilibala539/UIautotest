"""探索会话盒子 - 完整长按菜单"""
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

# Long press on a conversation that's lower in the list to get full popup above
# Let's target "工作日历" or "服务号" area - y around 270
# Actually, let's target the first non-pinned conversation, like y~375 area
# From previous scan: [167,375] "POPO助手" and [310,412] are in the same row

print("Step 1: Long press on POPO助手 conversation...")
# The "POPO助手" text is at [167,375], the row is around y=375-410
# Long press at y=390 (middle of that row)
x, y = 270, 390
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
               'input', 'swipe', str(x), str(y), str(x), str(y), '1500'], capture_output=True)
time.sleep(2)

result = aw.ocr_scan_page()
print("\n=== Context menu for POPO助手 ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/longpress_popo_assistant.png')

# Check if we can see all menu items
print("\n--- All menu-like items: ---")
for r in result:
    if r['cy'] > 300:  # menu items below the midpoint
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Close and try another conversation that's higher up, so popup shows below
aw.press_back()
time.sleep(1)

# Try long-pressing on the first conversation area (y around 270-310)
# From scan: [163,271] "工作日历" area
print("\n\nStep 2: Long press on first conversation row (y~290)...")
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
               'input', 'swipe', '270', '290', '270', '290', '1500'], capture_output=True)
time.sleep(2)

result2 = aw.ocr_scan_page()
print("\n=== Context menu for conversation at y=290 ===")
for r in result2:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/longpress_first_conv.png')

# Look for 会话盒子 or similar
print("\n--- Context menu analysis ---")
menu_items = []
for r in result2:
    text = r['text']
    if any(kw in text for kw in ['置顶', '取消置顶', '已读', '未读', '删除', '盒子', 
                                  '免打扰', '不显示', '添加', '待处理', '标为', '关闭',
                                  '消息提醒', '设为', '移入', '收纳']):
        menu_items.append(r)
        print(f"  MENU: \"{text}\" at [{r['cx']},{r['cy']}]")

# If the popup doesn't show "会话盒子", let's check if there's more to the menu
# Try scrolling within the popup
if menu_items:
    # Check max y of menu
    max_menu_y = max(r['cy'] for r in menu_items)
    print(f"\n  Menu extends to y={max_menu_y}")
    if max_menu_y > 850:
        print("  Menu may extend below screen, need to scroll")

# Close menu and try one more thing - check the "..." button
aw.press_back()
time.sleep(1)

# Try long pressing a different position for a more complete menu
print("\n\nStep 3: Long press lower in list (y~690)...")
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
               'input', 'swipe', '270', '690', '270', '690', '1500'], capture_output=True)
time.sleep(2)

result3 = aw.ocr_scan_page()
print("\n=== Context menu for conversation at y=690 ===")
for r in result3:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/longpress_lower_conv.png')

print("\n--- Menu items: ---")
for r in result3:
    if any(kw in r['text'] for kw in ['置顶', '取消', '已读', '未读', '删除', '盒子', 
                                       '免打扰', '不显示', '添加', '待处理', '标为', '关闭',
                                       '消息提醒', '设为', '移入', '收纳', '关闭提醒', '消息免打扰']):
        print(f"  MENU: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
