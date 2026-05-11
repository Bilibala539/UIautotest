"""探索会话分组 - 重启App后检查Tab栏 + 尝试从分组管理创建新分组"""
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

pos = aw.find_text_by_ocr("浮窗", timeout=3)
if pos:
    aw.click_text("取消", timeout=3)
    time.sleep(1)

# Check if tab bar appeared after restart
print("Step 1: Check message list after restart for 分组Tab...")
result = aw.ocr_scan_page()
print("Top area (y < 150):")
for r in result:
    if r['cy'] < 150:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

# Look for 皮皮 or other group tabs
for r in result:
    if any(kw in r['text'] for kw in ['皮皮', '全部', '分组', '最近']):
        print(f"  *** TAB FOUND: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/msg_list_restart_check.png')

# Since we still don't see tabs, let's check if the "会话分组" page has more options
# Maybe we need to also enter the page from the right-top "+" button to create a group
print("\n\nStep 2: Enter chat settings → 会话分组 and try '+' (top right)...")
pos = aw.find_text_by_ocr("工作日历", timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(3)

aw.tap(270, 70)  # settings
time.sleep(2)

pos = aw.find_text_by_ocr("会话分组", timeout=5)
if not pos:
    aw.swipe_up(distance=200)
    time.sleep(1)
    pos = aw.find_text_by_ocr("会话分组", timeout=5)

if pos:
    aw.tap(pos[0] + 100, pos[1])
    time.sleep(2)
    
    result2 = aw.ocr_scan_page()
    print("\n=== 会话分组 page (after add) ===")
    for r in result2:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    
    # Now we should see "该会话所属分组: 皮皮 ×"
    # Let's try the top-right "+" to see the add group interface
    print("\n\nStep 3: Click top-right '+' to add/manage groups...")
    aw.tap(408, 71)  # "+" button at top right
    time.sleep(2)
    
    result3 = aw.ocr_scan_page()
    print("\n=== After clicking '+' (top-right) ===")
    for r in result3:
        print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
    aw.take_screenshot(save_path='explorer_output/screenshots/session_group_add_page.png')
    
    # This might show a "新增分组" dialog or navigation to management page
    for r in result3:
        if any(kw in r['text'] for kw in ['新增', '创建', '分组名', '名称', '输入', '确定', '保存', '管理']):
            print(f"  *** ADD GROUP UI: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Check if it shows a list of all available groups (with + to add)
    for r in result3:
        if any(kw in r['text'] for kw in ['皮皮', '十', '+', '未读']):
            print(f"  Group item: \"{r['text']}\" at [{r['cx']},{r['cy']}]")
    
    # Also check - maybe this shows the management page that the test cases mention
    # "入口1: 点击会话分组栏-更多-管理" → this page might be it
    print("\n\nStep 4: Looking for 管理 button...")
    manage_pos = aw.find_text_by_ocr("管理", timeout=3)
    if manage_pos:
        print(f"  Found '管理' at {manage_pos}, clicking...")
        aw.tap(manage_pos[0], manage_pos[1])
        time.sleep(2)
        
        result4 = aw.ocr_scan_page()
        print("\n=== 分组管理 page ===")
        for r in result4:
            print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")
        aw.take_screenshot(save_path='explorer_output/screenshots/group_manage_page.png')
    else:
        # Try going to settings
        settings_pos = aw.find_text_by_ocr("设置", timeout=3)
        if settings_pos:
            print(f"  Found '设置' at {settings_pos}")
else:
    print("  '会话分组' not found")
