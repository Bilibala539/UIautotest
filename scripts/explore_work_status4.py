"""探索工作状态 - 消息列表页头像区域"""
import sys, os, logging, time, subprocess
sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
logging.basicConfig(level=logging.WARNING)
from utils.aw import create_aw
from utils.devices import get_adb, POPO_PACKAGE

aw = create_aw(platform='mumu', instance_id=0)

# Dismiss popup
print("Dismissing popup...")
aw.click_text("保持现状", timeout=5)
time.sleep(1)

# Back to message list
aw.click_text("消息", timeout=5)
time.sleep(2)

# Now look at the header - the sidebar entry is top-left
# Let's open sidebar again and look more carefully
print("\nStep 4: Re-open sidebar and look for status...")
aw.tap(27, 71)  # Top-left avatar/sidebar area
time.sleep(2)

result = aw.ocr_scan_page()
print("\nSidebar (full):")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] bbox={r.get('bbox')} \"{r['text']}\"")

# I see "工卡" in the sidebar at [389,206] from earlier
# That might be work badge/card, not work status
# Let's check if there's anything beneath the name that relates to status
# Previous sidebar showed: 
#   [82,204] "孟静娴"
#   [389,206] "工卡"
#   [102,252] "18498585468"
#   [211,286] "grp.popoqa67@corp.netease.com"
#   [181,328] "ink虐搜搜女兵土佐听涛了咯"
# No "work status" entry visible

# Maybe it's in Settings
print("\nStep 5: Go to Settings...")
aw.click_text("设置", timeout=5)
time.sleep(2)

result = aw.ocr_scan_page()
print("\nSettings page elements:")
for r in result:
    print(f"  [{r['cx']:3d},{r['cy']:3d}] \"{r['text']}\"")

status_kw = ['工作状态', '状态', '在线', '忙碌', '通用']
for r in result:
    for kw in status_kw:
        if kw in r['text']:
            print(f"\n  *** Found: \"{r['text']}\" at [{r['cx']},{r['cy']}]")

aw.take_screenshot(save_path='explorer_output/screenshots/settings_page.png')
