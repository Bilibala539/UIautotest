"""探索取消置顶功能 - 长按已置顶会话"""
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

# On the message list, there should be pinned contacts at the top
# First let's see what's there
print("Step 1: Message list - check for pinned items...")
result = aw.ocr_scan_page()
print("\nMessage list top area (y<250):")
for r in result:
    if r['cy'] < 250:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# The pinned contacts appear as avatars at the top (紫瑜, 白紫瑜, etc.)
# Let's long-press on one of the pinned contacts
# From previous exploration: pinned contacts are at y≈155-205
# 紫瑜 at [54, 154], 白紫瑜 at [55, 205]
print("\nStep 2: Long-press on pinned contact '紫瑜' at (54, 154)...")
# Use ADB long press (swipe from same point with duration)
subprocess.run([adb, '-s', '127.0.0.1:16384', 'shell', 'input', 'swipe', '54', '154', '54', '154', '1000'], capture_output=True)
time.sleep(2)

result = aw.ocr_scan_page()
print("\nAfter long-press (context menu?):")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Look for "取消置顶" option
for r in result:
    if '取消' in r['text'] or '置顶' in r['text'] or '删除' in r['text']:
        print(f"\n  *** Found: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/unpin_longpress.png')
