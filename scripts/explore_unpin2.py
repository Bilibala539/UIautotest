"""探索取消置顶 - 长按消息列表项"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)
adb = get_adb()

# Try long-pressing on the first message list item (a conversation)
# "工作日历服务号" at y≈270, or "POPO助手" at y≈375
# Let's try a longer duration and on a message item
print("Step 3: Long-press on conversation item 'POPO助手' area (270, 375)...")
# Use ADB input swipe with 2000ms duration for long press
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'input', 'swipe', 
                '270', '375', '270', '375', '2000'], capture_output=True)
time.sleep(2)

result = aw.ocr_scan_page()
print("\nAfter long-press on POPO助手 (context menu?):")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Check for menu items
menu_kw = ['置顶', '取消置顶', '已读', '未读', '删除', '免打扰', '标记', '屏蔽']
print("\n--- Menu keywords found: ---")
for r in result:
    for kw in menu_kw:
        if kw in r['text']:
            print(f"  Found \"{kw}\" in \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/longpress_conversation.png')
