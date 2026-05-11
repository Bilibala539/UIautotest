"""探索会话盒子 - 滑动长按菜单看完整选项"""
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

# Long press on a higher-up conversation so the menu can show more items below
# Let me use "工作日历" at the top
print("Step 1: Long press on first conversation row...")
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
               'input', 'swipe', '270', '290', '270', '290', '1500'], capture_output=True)
time.sleep(2)

# Take screenshot and check
aw.take_screenshot(save_path='explorer_output/screenshots/longpress_menu_full.png')

# Now try swiping up within the menu area to see more options
print("Step 2: Swiping up within menu...")
subprocess.run([adb_path, '-s', '127.0.0.1:16384', 'shell', 
               'input', 'swipe', '270', '910', '270', '750', '300'], capture_output=True)
time.sleep(1)

result = aw.ocr_scan_page()
print("\n=== After swiping menu up ===")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/longpress_menu_scrolled.png')

# Try pressing on the "口" area (possible checkbox), to see if it's a "more" menu
# Close and try a different approach - look at the bottom action sheet
aw.press_back()
time.sleep(1)

# New approach: 这个菜单看起来是一个底部弹出的 action sheet
# 标准格式是: [取消置顶/置顶] + [添加到待处理] + 可能的更多选项
# 如果菜单只有这两项，说明"会话盒子"功能入口不在长按菜单里

# Let's try: go into a P2P chat settings to look for "会话盒子" option
print("\n\nStep 3: Checking P2P chat settings for 会话盒子 option...")
# Enter a P2P conversation
pos = aw.find_text_by_ocr("孟龄钊", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(2)
else:
    # Try clicking on the chat name
    aw.tap(270, 480)
    time.sleep(2)

# Now in chat page, click the top bar to enter settings
# Chat page has a name at top center
result2 = aw.ocr_scan_page()
print("\n=== Chat page ===")
for r in result2:
    if r['cy'] < 100:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Look for "群成员" or chat name at top
# Click on the chat name area at top to enter settings
aw.tap(270, 70)
time.sleep(2)

result3 = aw.ocr_scan_page()
print("\n=== Chat/Group settings page ===")
for r in result3:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
aw.take_screenshot(save_path='explorer_output/screenshots/chat_settings_for_box.png')

# Look for "会话盒子" or "消息提醒" settings
print("\n--- Looking for 会话盒子 in settings ---")
for r in result3:
    if any(kw in r['text'] for kw in ['会话盒子', '盒子', '消息提醒', '免打扰', '静音', '关闭提醒', '关闭消息']):
        print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

# Scroll to see more settings
aw.swipe_up(distance=300)
time.sleep(1)
result4 = aw.ocr_scan_page()
print("\n=== Settings after scroll ===")
for r in result4:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

for r in result4:
    if any(kw in r['text'] for kw in ['会话盒子', '盒子', '消息提醒', '免打扰', '静音', '关闭提醒', '关闭消息', '添加到']):
        print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/chat_settings_scrolled.png')

# One more scroll
aw.swipe_up(distance=300)
time.sleep(1)
result5 = aw.ocr_scan_page()
print("\n=== Settings after 2nd scroll ===")
for r in result5:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
for r in result5:
    if any(kw in r['text'] for kw in ['会话盒子', '盒子', '消息提醒', '免打扰', '静音', '关闭提醒', '关闭消息']):
        print(f"  FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
