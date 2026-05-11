"""探索当前消息列表页面的完整状态"""
import sys, os, logging, cv2, numpy as np, subprocess, time
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from image.image_name_mapping import MESSAGE_TAB_BLUE

aw = create_aw(platform='mumu', instance_id=0)

# Start POPO
from utils.devices import get_adb, POPO_PACKAGE
adb = get_adb()
subprocess.run([adb, '-s', '127.0.0.1:16384',
                'shell', 'monkey', '-p', POPO_PACKAGE,
                '-c', 'android.intent.category.LAUNCHER', '1'], capture_output=True)
time.sleep(8)

# Check message page
pos = aw.find_image(MESSAGE_TAB_BLUE, timeout=15)
print(f'On message page: {pos is not None}')

# Take screenshot
img = aw.take_screenshot(save_path='explorer_output/screenshots/fresh_msg_page.png')
print(f'Screenshot shape: {img.shape}')

# Full OCR scan
result = aw.ocr_scan_page()
print('\nFull page OCR:')
for r in result:
    text = r['text']
    cx = r['cx']
    cy = r['cy']
    bbox = r['bbox']
    print(f'  [{cx:3d},{cy:3d}] bbox={bbox} "{text}"')

# Save specific regions for element cropping
# Header area (y=50-100): title + icons
header = img[50:100, :, :]
cv2.imwrite('explorer_output/screenshots/header_area.png', header)

# Below header (y=92-250): pinned area + possible tab bar
below_header = img[92:260, :, :]
cv2.imwrite('explorer_output/screenshots/below_header_area.png', below_header)

# Look for the "≡" icon or any icon to the right of tab names
# Check x=480-540, y=90-130 area (right side of potential tab bar)
right_icon_area = img[85:135, 480:540, :]
cv2.imwrite('explorer_output/screenshots/right_icon_area.png', right_icon_area)
avg = np.mean(right_icon_area)
print(f'\nRight icon area (x=480-540, y=85-135) avg brightness: {avg:.1f}')

# Check if there are any non-white elements in right icon area
non_white_pixels = np.sum(right_icon_area.mean(axis=2) < 200)
total_pixels = right_icon_area.shape[0] * right_icon_area.shape[1]
print(f'Non-white pixels: {non_white_pixels}/{total_pixels} ({100*non_white_pixels/total_pixels:.1f}%)')
