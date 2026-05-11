"""回到消息列表页准备测试"""
import sys
sys.path.insert(0, "E:\\UIAutotest")

from utils.aw import create_aw

aw = create_aw(platform="mumu", instance_id=0)

# 从WorkHub按返回回到消息列表
aw.press_back()
aw.sleep(2)

# 检查当前状态
results = aw.ocr_scan_page()
texts = [r['text'] for r in results]
with open("explorer_output/current_state.txt", "w", encoding="utf-8") as f:
    for t in texts:
        f.write(f"  {t}\n")
    has_msg_tab = any("消息" == t for t in texts) or any("工作台" in t for t in texts)
    f.write(f"\n在消息列表: {has_msg_tab}")

# 从消息列表返回
aw.click_text("取消", timeout=3)
aw.sleep(2)

# 现在在消息列表页，彩色圆环在搜索按钮左侧
# 搜索按钮x=430，彩色圆环应该在x=380左右
# 但是380之前试过不行，可能更靠左
# 让我试 x=350, y=72
aw.tap(350, 72)
aw.sleep(5)

results = aw.ocr_scan_page()
with open("explorer_output/tap_350_72.txt", "w", encoding="utf-8") as f:
    f.write("=== 点击(350, 72)后 ===\n")
    for r in results:
        bbox = r['bbox']
        f.write(f"  {r['text']} @ ({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})\n")
    has_workhub = any("WorkHub" in r['text'] for r in results)
    f.write(f"\nWorkHub: {has_workhub}\n")