"""Analyze long press screenshot"""
import cv2, numpy as np, sys, os
sys.stdout.reconfigure(encoding='utf-8')
img = cv2.imdecode(np.fromfile(r'E:\UIAutotest\screenshots\debug_lp_chat.png', dtype=np.uint8), cv2.IMREAD_COLOR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Find dark areas (potential menu)
dark = gray < 100
di = np.where(dark)
print(f"Dark pixels (<100): {dark.sum()}")
if dark.sum() > 0:
    print(f"Y range: {di[0].min()}-{di[0].max()}")
    print(f"X range: {di[1].min()}-{di[1].max()}")
    
    # Group by y
    ys = sorted(set(di[0].tolist()))
    groups = []
    curr = []
    prev = -10
    for y in ys:
        if y - prev > 5:
            if curr:
                groups.append(curr)
            curr = [y]
        else:
            curr.append(y)
        prev = y
    if curr:
        groups.append(curr)
    
    print(f"\nDark clusters ({len(groups)} total, showing first 10):")
    for g in groups[:10]:
        mask = (di[0] >= g[0]) & (di[0] <= g[-1])
        xs = di[1][mask]
        count = mask.sum()
        print(f"  y={g[0]}-{g[-1]}, x={xs.min()}-{xs.max()}, pixels={count}")

# Also check for medium-dark (potential menu background 50-150 gray)
medium = (gray >= 50) & (gray < 150)
mi = np.where(medium)
print(f"\nMedium pixels (50-150): {medium.sum()}")
if medium.sum() > 100:
    print(f"Y range: {mi[0].min()}-{mi[0].max()}")
    print(f"X range: {mi[1].min()}-{mi[1].max()}")
    
    # Check if there's a rectangular cluster (menu popup)
    # Look for a concentrated area
    for y_start in range(0, 960, 100):
        y_end = y_start + 100
        region = medium[y_start:y_end, :]
        if region.sum() > 500:
            print(f"  Concentration at y={y_start}-{y_end}: {region.sum()} pixels")
