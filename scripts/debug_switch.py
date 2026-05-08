"""Debug script to analyze switch detection issue"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import cv2
import numpy as np
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.aw_base import AWBase

driver = MuMuDriver(instance_id=0)
aw = AWBase(driver)

# Read the failure screenshot
with open(r'E:\UIAutotest\screenshots\FAIL_test_toggle_auto_download_file_20260430_205157.png', 'rb') as f:
    data = np.frombuffer(f.read(), np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

print(f"Image shape: {img.shape}")

# Run OCR on this image
ocr = aw._get_ocr_engine()
result = ocr.predict(img)

ocr_results = []
for page in result:
    texts = page.get('rec_texts', [])
    polys = page.get('dt_polys', [])
    for i, text in enumerate(texts):
        if polys is not None and i < len(polys):
            poly = polys[i]
            cx = int(np.mean([p[0] for p in poly]))
            cy = int(np.mean([p[1] for p in poly]))
            ocr_results.append((text, cx, cy))

print("\nAll OCR results:")
for text, cx, cy in sorted(ocr_results, key=lambda x: x[2]):
    print(f"  y={cy:3d} x={cx:3d}: '{text}'")

# Now find ALL switch-like colored areas (blue or grey toggle)
b, g, r = img[:,:,0].astype(int), img[:,:,1].astype(int), img[:,:,2].astype(int)

# Blue switch detection (ON state)
blue_mask = (b > 200) & (g > 100) & (g < 180) & (r < 100)
print(f"\nTotal blue pixels: {blue_mask.sum()}")

# Grey/white switch detection (OFF state) - typically a light grey oval
# Let's just scan the right side (x>400) for non-white non-background content
print("\n=== Analyzing switch column (x=400-530) for each text row ===")
switch_texts = ['文件自动下载', '消息气泡聚合显示', '分享转发时需再次确认', '启用表情联想']
for text, cx, cy in ocr_results:
    if text in switch_texts:
        # Check if there are blue pixels in a wider y range around this text
        # Try y-5 to y+30 (switch might be below or level with text)
        for dy_range in [20, 30, 40, 50]:
            scan_y1 = max(0, cy - dy_range)
            scan_y2 = min(img.shape[0], cy + dy_range)
            scan_region = img[scan_y1:scan_y2, 400:530]
            sb, sg, sr = scan_region[:,:,0].astype(int), scan_region[:,:,1].astype(int), scan_region[:,:,2].astype(int)
            blue_count = ((sb > 200) & (sg > 100) & (sg < 180) & (sr < 100)).sum()
            if blue_count > 0:
                print(f"  '{text}' y={cy}: BLUE found with dy_range=±{dy_range} ({blue_count} pixels)")
                break
        else:
            print(f"  '{text}' y={cy}: NO blue even with ±50")
        
        # Check what's at x=460-500 in this row (the actual toggle location)
        row_slice = img[max(0,cy-5):cy+5, 460:510]
        avg_b = row_slice[:,:,0].mean()
        avg_g = row_slice[:,:,1].mean()
        avg_r = row_slice[:,:,2].mean()
        print(f"    At text level (y={cy}±5, x=460-510): avg BGR=({avg_b:.0f},{avg_g:.0f},{avg_r:.0f})")

# Key insight: check where the switch toggles actually are on the page
print("\n=== All blue pixel clusters (excluding status bar) ===")
if blue_mask.sum() > 0:
    bi = np.where(blue_mask)
    # Filter out status bar (y < 50)
    valid = bi[0] > 50
    if valid.sum() > 0:
        y_vals = bi[0][valid]
        x_vals = bi[1][valid]
        print(f"Blue Y range (excl status bar): {y_vals.min()}-{y_vals.max()}")
        print(f"Blue X range: {x_vals.min()}-{x_vals.max()}")
        # For each unique y cluster
        prev_y = -10
        for y in sorted(set(y_vals.tolist())):
            if y - prev_y > 3:
                # New cluster
                cluster_mask = (bi[0] >= y) & (bi[0] < y + 40) & (bi[0] > 50)
                cluster_count = cluster_mask.sum()
                if cluster_count > 50:
                    cluster_x = bi[1][cluster_mask]
                    print(f"  Cluster at y~{y}: x={cluster_x.min()}-{cluster_x.max()}, pixels={cluster_count}")
                    # Which text is closest to this y?
                    closest = min(ocr_results, key=lambda t: abs(t[2] - y))
                    print(f"    Closest text: '{closest[0]}' at y={closest[2]} (diff={y - closest[2]})")
            prev_y = y
