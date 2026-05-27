"""
Re-capture 7 outdated UI element images from MuMu emulator.
Saves new screenshots to image_ai/ directory.
"""
import subprocess
import os
import time
import numpy as np
from PIL import Image, ImageFilter

ADB = r"C:\Program Files\Netease\MuMu\nx_main\adb.exe"
DEVICE = "127.0.0.1:16384"
SCREENSHOT_DIR = r"E:\UIAutotest\output\screenshots"
OUTPUT_DIR = r"E:\UIAutotest\image_ai"
W, H = 540, 960

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def adb(cmd: str) -> str:
    """Run ADB command and return stdout."""
    full = f'"{ADB}" -s {DEVICE} {cmd}'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=15)
    if r.returncode != 0 and r.stderr.strip():
        print(f"  [ADB warn] {r.stderr.strip()}")
    return r.stdout.strip()


def tap(x: int, y: int):
    adb(f"shell input tap {x} {y}")


def swipe(x1: int, y1: int, x2: int, y2: int, duration: int = 300):
    adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")


def back():
    adb("shell input keyevent 4")


def screenshot(name: str = "temp") -> str:
    """Take screenshot and pull to local. Returns local path."""
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    adb("shell screencap -p /data/local/tmp/s.png")
    adb(f"pull /data/local/tmp/s.png {path}")
    return path


def load_img(path: str) -> Image.Image:
    return Image.open(path).convert("RGB")


def quality_check(img: Image.Image, min_std: float = 5.0, min_size: int = 10) -> bool:
    """Check image quality: grayscale std > min_std, mean in 5-250, min dimension >= 10."""
    gray = np.array(img.convert("L"))
    mean_val = gray.mean()
    std_val = gray.std()
    w, h = img.size
    ok = True
    if std_val < min_std:
        print(f"    FAIL: std={std_val:.1f} < {min_std}")
        ok = False
    if mean_val < 5 or mean_val > 250:
        print(f"    FAIL: mean={mean_val:.1f} out of [5, 250]")
        ok = False
    if w < min_size or h < min_size:
        print(f"    FAIL: size={w}x{h} below {min_size}x{min_size}")
        ok = False
    if ok:
        print(f"    PASS: {w}x{h}, mean={mean_val:.1f}, std={std_val:.1f}")
    return ok


def detect_bottom_tab_colors(img: Image.Image):
    """Return list of (x_center, r_mean, g_mean, b_mean) for bottom tab bar region."""
    # Bottom bar is roughly y=900-960
    bar = img.crop((0, 900, W, 960))
    arr = np.array(bar)
    tabs = []
    # 5 tabs, each ~108px wide
    for i in range(5):
        cx = 54 + i * 108
        x0 = max(0, cx - 30)
        x1 = min(W, cx + 30)
        region = arr[:, x0:x1, :]
        r = region[:, :, 0].mean()
        g = region[:, :, 1].mean()
        b = region[:, :, 2].mean()
        tabs.append((cx, r, g, b))
    return tabs


def is_color_blue(r: float, g: float, b: float) -> bool:
    """Detect if a region is predominantly blue (active tab)."""
    return b > r + 15 and b > g + 10


def navigate_to_message_page():
    """Ensure we're on the message page (first tab active)."""
    print("[Nav] Navigating to message page...")
    # Try going to message page by tapping first tab
    # Launch app fresh
    adb("shell am start -n com.netease.popo/.login.ui.SplashActivity")
    time.sleep(4)

    # Take screenshot and check
    for attempt in range(5):
        screenshot("nav_check")
        img = load_img(os.path.join(SCREENSHOT_DIR, "nav_check.png"))
        tabs = detect_bottom_tab_colors(img)
        # Check if message tab (index 0) is blue (active)
        cx, r, g, b = tabs[0]
        print(f"  Tab0: rgb=({r:.0f},{g:.0f},{b:.0f}), Tab4: rgb=({tabs[4][1]:.0f},{tabs[4][2]:.0f},{tabs[4][3]:.0f})")
        if is_color_blue(r, g, b):
            print("  Message tab is active (blue).")
            return
        # Tap message tab
        print(f"  Attempt {attempt+1}: tapping message tab...")
        tap(54, 930)
        time.sleep(1.5)

    print("  Warning: Could not confirm message page, proceeding anyway.")
    tap(54, 930)
    time.sleep(1)


def navigate_to_contacts_page():
    """Navigate: message page -> more tab -> contacts entry."""
    print("[Nav] Navigating to contacts page...")
    # First ensure message page
    adb("shell am start -n com.netease.popo/.login.ui.SplashActivity")
    time.sleep(3)

    # Tap "更多" tab (5th tab, rightmost)
    more_x, more_y = 486, 930
    tap(more_x, more_y)
    time.sleep(1)

    # Now we should see the "更多" menu with "通讯录" entry
    # Take screenshot to verify
    screenshot("more_menu")
    img = load_img(os.path.join(SCREENSHOT_DIR, "more_menu.png"))

    # Try to find the 通讯录 entry in the menu
    # It's usually the first or second item in the more menu
    # Typical position: y around 200-350 area
    # Let's check for text regions in that area
    arr = np.array(img)

    # Analyze the menu region (upper half)
    menu_region = arr[100:500, 50:490, :]
    gray_menu = np.mean(menu_region, axis=2)

    # Find rows that have significant dark content (text)
    row_means = gray_menu.mean(axis=1)
    text_rows = np.where(row_means < 200)[0]

    if len(text_rows) > 0:
        print(f"  Found {len(text_rows)} rows with text content in menu area")

    # Tap where 通讯录 should be — typically first menu item
    # Let's try a grid tap approach: click the area around (270, 250)
    contacts_tap_x, contacts_tap_y = 270, 280
    tap(contacts_tap_x, contacts_tap_y)
    time.sleep(1.5)

    # Take screenshot to verify we're on contacts page
    screenshot("contacts_page")
    print("  Contacts page screenshot saved.")


def navigate_to_sidebar():
    """Navigate: message page -> tap avatar top-left."""
    print("[Nav] Navigating to sidebar...")
    # Go back to message page first
    adb("shell am start -n com.netease.popo/.login.ui.SplashActivity")
    time.sleep(3)

    # Tap avatar at top-left (~25, 75)
    tap(25, 75)
    time.sleep(1.5)

    screenshot("sidebar_page")
    print("  Sidebar screenshot saved.")


def navigate_to_elife_page():
    """Navigate: message page -> elife tab."""
    print("[Nav] Navigating to elife page...")
    # Go back to message page
    adb("shell am start -n com.netease.popo/.login.ui.SplashActivity")
    time.sleep(3)

    # Tap 易生活 tab (4th tab)
    tap(378, 930)
    time.sleep(2)

    screenshot("elife_page")
    print("  Elife page screenshot saved.")


def find_horizontal_lines(arr_gray: np.ndarray, threshold: int = 30) -> list:
    """Find horizontal separator lines (rows with low variance and distinct color)."""
    h, w = arr_gray.shape
    lines = []
    for y in range(h):
        row_std = arr_gray[y, :].std()
        if row_std < threshold:
            # Low variance = likely a solid line
            lines.append(y)
    return lines


def find_vertical_region(arr: np.ndarray, y_start: int, y_end: int,
                         target_color_range=None) -> tuple:
    """Find the vertical extent of a region containing specific content."""
    region = arr[y_start:y_end, :]
    gray = np.mean(region, axis=2) if len(region.shape) == 3 else region

    col_means = gray.mean(axis=0)
    # Find columns with content (darker than background)
    has_content = col_means < np.percentile(col_means, 90) - 10
    content_cols = np.where(has_content)[0]

    if len(content_cols) > 0:
        return content_cols[0], content_cols[-1]
    return 0, W


def crop_contacts_elements():
    """Crop 4 elements from contacts page screenshot."""
    img_path = os.path.join(SCREENSHOT_DIR, "contacts_page.png")
    img = load_img(img_path)
    arr = np.array(img)
    gray = np.array(img.convert("L"))

    results = []

    # Analyze the page structure
    # Top bar: y=0-90 (通讯录 title, search, add)
    # Entry list: typically starts around y=120
    # Bottom nav: y=900-960

    # Find horizontal edges/transitions in the content area
    row_diffs = np.abs(np.diff(gray[100:850, :].mean(axis=1)))
    # Find significant transitions
    transitions = np.where(row_diffs > 8)[0] + 100

    print(f"  Found {len(transitions)} significant row transitions")

    # Heuristic: the 3 list entries (联系人分组, 群组, 服务号) are in the upper portion
    # Each entry is roughly 60-70px tall with an icon on the left and text
    # Let's scan for rows that look like list item separators

    # Try to identify 3 entry rows by looking at color distribution
    # The entries typically have:
    #   - Left icon region: x=10-60
    #   - Text region: x=70-200
    #   - Arrow/navigation indicator on right

    # Scan y from 100 to 600 looking for entry patterns
    entry_candidates = []

    for y in range(100, 600, 5):
        # Check if this row has the pattern of a list entry
        # Left side has icon (distinct color patch), right side has text
        left_region = arr[y-20:y+20, 10:60, :]
        text_region = arr[y-20:y+20, 70:250, :]
        right_region = arr[y-20:y+20, 400:530, :]

        left_std = left_region.std(axis=(0, 1)).mean()
        text_std = text_region.std(axis=(0, 1)).mean()

        # List entries have structured content
        if left_std > 20:
            # Check if there's a distinct transition above and below (cell borders)
            above_gray = gray[max(0, y-35):y-15, 50:490].mean()
            mid_gray = gray[y-15:y+15, 50:490].mean()
            below_gray = gray[y+15:y+35, 50:490].mean()

            # Wait, let me just do a simpler approach
            pass

    # Simpler approach: scan for rows with text content patterns
    # The contacts page has entries in a list, each with:
    # - An icon on the left (~x=25-55)
    # - A text label (~x=70-200)
    # - A right arrow/indicator (~x=490-520)

    # Find the 3 entry groups
    # Each entry group has a distinct icon color region

    # Let's just use fixed coordinates based on layout analysis
    # For contacts page on 540x960, the entries are typically:
    # Entry 1 (联系人分组): ~y=180-250
    # Entry 2 (群组): ~y=250-320
    # Entry 3 (服务号): ~y=320-390

    # But these are guesses. Let me be smarter - scan for the entries.

    # Analyze rows to find content blocks
    row_var = np.array([gray[y, 50:490].std() for y in range(100, 800)])
    # High variance = content, low variance = whitespace/separators
    content_mask = row_var > 8

    # Find contiguous content blocks
    blocks = []
    in_block = False
    block_start = 0
    for i, has_content in enumerate(content_mask):
        y = i + 100
        if has_content and not in_block:
            block_start = y
            in_block = True
        elif not has_content and in_block:
            block_h = y - block_start
            if 30 < block_h < 100:  # Entry-sized block
                blocks.append((block_start, y))
            in_block = False
    if in_block:
        y = len(content_mask) + 100
        block_h = y - block_start
        if 30 < block_h < 100:
            blocks.append((block_start, y))

    print(f"  Found {len(blocks)} content blocks in entry area")
    for i, (y0, y1) in enumerate(blocks[:5]):
        print(f"    Block {i}: y={y0}-{y1} (h={y1-y0})")

    # Now identify which blocks correspond to the 3 entries
    # Look for blocks that have left-side color (icon) + right-side content
    entry_blocks = []
    for y0, y1 in blocks:
        # Check if there's icon content on the left
        left_icon_region = gray[y0:y1, 15:55]
        left_std = left_icon_region.std()
        # Check if there's text content in the middle
        text_region = gray[y0:y1, 60:300]
        text_std = text_region.std()

        if left_std > 15 and text_std > 10:
            entry_blocks.append((y0, y1))
            print(f"    Entry candidate: y={y0}-{y1}, left_std={left_std:.1f}, text_std={text_std:.1f}")

    # We need exactly 3 entries: 联系人分组, 群组, 服务号
    # If we found more or fewer, use best guess coordinates
    if len(entry_blocks) >= 3:
        entry_blocks = entry_blocks[:3]
    else:
        print("  Using estimated entry positions")
        # Estimate based on typical layout
        entry_blocks = [(150, 220), (220, 290), (290, 360)]

    # Crop entry elements (icon + text, NO arrow indicator)
    entry_names = [
        ("通讯录页-联系人分组入口.png", "CONTACTS_GROUP_ENTRY"),
        ("通讯录页-群组入口.png", "CONTACTS_TEAM_ENTRY"),
        ("通讯录页-服务号入口.png", "CONTACTS_SERVICE_ENTRY"),
    ]

    for i, (name, const_name) in enumerate(entry_names):
        if i < len(entry_blocks):
            y0, y1 = entry_blocks[i]
            # Crop: left icon area + text, avoid right arrow
            # Tight crop: icon x=15-55, text x=55-280
            cropped = img.crop((15, y0, 280, y1))
        else:
            # Fallback
            y0 = 150 + i * 70
            cropped = img.crop((15, y0, 280, y0 + 70))

        save_path = os.path.join(OUTPUT_DIR, name)
        cropped.save(save_path)
        ok = quality_check(cropped)
        results.append((name, save_path, ok))

    # Crop alphabet bar (right side, A-Z index)
    # Alphabet bar is typically on the right edge
    # Scan for the vertical bar on the right side of the screen
    right_col_var = np.array([gray[:, x].std() for x in range(W)])
    # Find the rightmost column range with significant variation
    right_content = np.where(right_col_var > 10)[0]
    right_content = right_content[right_content > 480]  # Right quarter of screen

    if len(right_content) > 0:
        x0 = right_content[0] - 2
        x1 = min(right_content[-1] + 2, W)
    else:
        x0, x1 = 515, 540

    # The alphabet bar spans most of the contacts list vertically
    # Find its vertical extent
    alpha_y0 = 120
    alpha_y1 = 850

    cropped = img.crop((x0, alpha_y0, x1, alpha_y1))
    name = "通讯录页-字母索引栏.png"
    save_path = os.path.join(OUTPUT_DIR, name)
    cropped.save(save_path)
    ok = quality_check(cropped)
    results.append((name, save_path, ok))

    return results


def crop_sidebar_element():
    """Crop SIDEBAR_DEVICE_MANAGEMENT from sidebar screenshot."""
    img_path = os.path.join(SCREENSHOT_DIR, "sidebar_page.png")
    img = load_img(img_path)
    gray = np.array(img.convert("L"))

    results = []

    # Sidebar layout:
    # - Avatar + name at top (~y=50-180)
    # - Function list starts around y=200
    # Items typically: 我的收藏, 服务台, 登录设备管理, 设置, etc.

    # Scan for list items
    row_var = np.array([gray[y, 50:490].std() for y in range(150, 700)])
    content_mask = row_var > 8

    blocks = []
    in_block = False
    block_start = 0
    for i, has_content in enumerate(content_mask):
        y = i + 150
        if has_content and not in_block:
            block_start = y
            in_block = True
        elif not has_content and in_block:
            block_h = y - block_start
            if 25 < block_h < 100:
                blocks.append((block_start, y))
            in_block = False
    if in_block:
        block_h = (len(content_mask) + 150) - block_start
        if 25 < block_h < 100:
            blocks.append((block_start, len(content_mask) + 150))

    print(f"  Sidebar: Found {len(blocks)} content blocks")
    for i, (y0, y1) in enumerate(blocks[:8]):
        print(f"    Block {i}: y={y0}-{y1} (h={y1-y0})")

    # 登录设备管理 is the 3rd item (after 我的收藏, 服务台/帮助与反馈)
    # It should also show a device count like "3"
    # Try to find it: it has an icon on the left + text + possibly a badge/number

    device_entry_idx = None
    for i, (y0, y1) in enumerate(blocks):
        # Check for text content in the middle region
        text_region = gray[y0:y1, 60:300]
        text_std = text_region.std()
        if text_std > 15:
            # Look for device count badge (usually a small colored circle with number)
            badge_region = gray[y0:y1, 350:500]
            badge_std = badge_region.std()
            if badge_std > 20:
                # This could be the device management entry with count
                device_entry_idx = i
                print(f"    Device management candidate: block {i} with badge_std={badge_std:.1f}")

    if device_entry_idx is not None:
        y0, y1 = blocks[device_entry_idx]
    elif len(blocks) >= 3:
        # Use 3rd block as fallback
        y0, y1 = blocks[2]
    else:
        # Hard fallback
        y0, y1 = 320, 390

    # Crop: icon + text, tight bounds
    # Avoid cropping the right arrow indicator, but include device count badge
    cropped = img.crop((15, y0, 510, y1))

    name = "侧边栏-登录设备管理.png"
    save_path = os.path.join(OUTPUT_DIR, name)
    cropped.save(save_path)
    ok = quality_check(cropped)
    results.append((name, save_path, ok))

    return results


def crop_elife_elements():
    """Crop 2 elements from elife page screenshot."""
    img_path = os.path.join(SCREENSHOT_DIR, "elife_page.png")
    img = load_img(img_path)
    arr = np.array(img)
    gray = np.array(img.convert("L"))

    results = []

    # Elife page layout:
    # - Top bar: y=0-90
    # - Content area: various cards
    # - Bottom nav: y=900-960

    # 1. More button (右上角) - typically a "..." or menu icon
    # Usually at top-right, around x=480-530, y=30-80
    # Let's detect the top bar right region
    top_right = arr[0:90, 440:540, :]
    # Find where the colored content starts (non-white background)
    tr_gray = gray[0:90, 440:540]
    content_cols = np.where(tr_gray.mean(axis=0) < 220)[0]

    if len(content_cols) > 0:
        more_x0 = 440 + content_cols[0] - 3
        more_x1 = 440 + content_cols[-1] + 3
    else:
        more_x0, more_x1 = 475, 530

    content_rows = np.where(tr_gray.mean(axis=1) < 220)[0]
    if len(content_rows) > 0:
        more_y0 = content_rows[0] - 2
        more_y1 = content_rows[-1] + 2
    else:
        more_y0, more_y1 = 25, 75

    cropped = img.crop((more_x0, more_y0, more_x1, more_y1))
    name = "易生活页-更多按钮.png"
    save_path = os.path.join(OUTPUT_DIR, name)
    cropped.save(save_path)
    ok = quality_check(cropped)
    results.append((name, save_path, ok))

    # 2. Floating icon (右下角浮窗)
    # Floating button is typically in the bottom-right corner, above the nav bar
    # Usually around x=440-520, y=780-880
    # Detect by looking for a distinct colored region in bottom-right
    float_region = gray[700:900, 400:540]

    # Find non-background content
    fr_mean = float_region.mean()
    fr_std_cols = np.array([float_region[:, x].std() for x in range(140)])
    fr_std_rows = np.array([float_region[y, :].std() for y in range(200)])

    content_x = np.where(fr_std_cols > 8)[0]
    content_y = np.where(fr_std_rows > 8)[0]

    if len(content_x) > 0 and len(content_y) > 0:
        fx0 = 400 + content_x[0] - 5
        fx1 = 400 + content_x[-1] + 5
        fy0 = 700 + content_y[0] - 5
        fy1 = 700 + content_y[-1] + 5
    else:
        # Fallback: common floating button position
        fx0, fy0, fx1, fy1 = 440, 780, 520, 880

    cropped = img.crop((fx0, fy0, fx1, fy1))
    name = "易生活页-浮窗图标.png"
    save_path = os.path.join(OUTPUT_DIR, name)
    cropped.save(save_path)
    ok = quality_check(cropped)
    results.append((name, save_path, ok))

    return results


def update_mapping():
    """Update image_name_mapping.py to point CONTACTS_*, SIDEBAR_DEVICE_MANAGEMENT, ELIFE_* to test_path."""
    mapping_path = r"E:\UIAutotest\image\image_name_mapping.py"
    with open(mapping_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Paths to update: these 7 constants currently use `path` but should use `test_path`
    updates = {
        "CONTACTS_GROUP_ENTRY = os.path.join(path,": "CONTACTS_GROUP_ENTRY = os.path.join(test_path,",
        "CONTACTS_TEAM_ENTRY = os.path.join(path,": "CONTACTS_TEAM_ENTRY = os.path.join(test_path,",
        "CONTACTS_SERVICE_ENTRY = os.path.join(path,": "CONTACTS_SERVICE_ENTRY = os.path.join(test_path,",
        "CONTACTS_ALPHABET_BAR = os.path.join(path,": "CONTACTS_ALPHABET_BAR = os.path.join(test_path,",
        "SIDEBAR_DEVICE_MANAGEMENT = os.path.join(path,": "SIDEBAR_DEVICE_MANAGEMENT = os.path.join(test_path,",
        "ELIFE_MORE_BUTTON = os.path.join(path,": "ELIFE_MORE_BUTTON = os.path.join(test_path,",
        "ELIFE_FLOATING_ICON = os.path.join(path,": "ELIFE_FLOATING_ICON = os.path.join(test_path,",
    }

    modified = False
    for old, new in updates.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"  Updated: {old.split('=')[0].strip()}")

    if modified:
        with open(mapping_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("  Mapping file updated.")
    else:
        print("  No mapping changes needed (already using test_path or not found).")


def main():
    print("=" * 60)
    print("Re-capturing 7 outdated UI element images")
    print("=" * 60)

    all_results = []

    # Step 1: Contacts page (4 elements)
    print("\n[Step 1/3] Contacts page...")
    navigate_to_contacts_page()
    results1 = crop_contacts_elements()
    all_results.extend(results1)

    # Step 2: Sidebar (1 element)
    print("\n[Step 2/3] Sidebar...")
    navigate_to_sidebar()
    results2 = crop_sidebar_element()
    all_results.extend(results2)

    # Step 3: Elife page (2 elements)
    print("\n[Step 3/3] Elife page...")
    navigate_to_elife_page()
    results3 = crop_elife_elements()
    all_results.extend(results3)

    # Summary
    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)
    passed = sum(1 for _, _, ok in all_results if ok)
    failed = sum(1 for _, _, ok in all_results if not ok)

    for name, path, ok in all_results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")

    print(f"\n  Total: {len(all_results)} images, {passed} passed, {failed} failed")

    if failed == 0:
        print("\nUpdating image_name_mapping.py...")
        update_mapping()

    print("\n[DONE]")


if __name__ == "__main__":
    main()
