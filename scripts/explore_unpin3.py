"""快速验证取消置顶 - 确认长按行为"""
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

# OCR current page to confirm we're on message list
result = aw.ocr_scan_page()
print("Current page - message list items (y=230-870):")
for r in result:
    if 230 < r['cy'] < 870:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Use long_press_text with region to find POPO助手 in message list area
print("\n\nNow try long_press_text with region=(0, 230, 540, 730)...")
try:
    pos = aw.find_text_by_ocr("POPO助手", timeout=5, region=(0, 230, 540, 730))
    print(f"Found 'POPO助手' at: {pos}")
except Exception as e:
    print(f"Failed to find 'POPO助手': {e}")
    # Try "工作日历" instead
    print("\nTrying '工作日历' instead...")
    pos = aw.find_text_by_ocr("工作日历", timeout=5, region=(0, 230, 540, 730))
    print(f"Found '工作日历' at: {pos}")

# Now long-press using AWBase
print("\nExecuting long press...")
aw.long_press_text("POPO助手", duration=2.0, region=(0, 230, 540, 730))
time.sleep(2)

# Check what appears
result = aw.ocr_scan_page()
print("\nAfter long press:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

aw.take_screenshot(save_path='explorer_output/screenshots/unpin_longpress_v2.png')
