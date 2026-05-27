"""重新启动POPO并回到消息列表页"""
import sys
sys.path.insert(0, "E:\\UIAutotest")

from utils.aw import create_aw

aw = create_aw(instance_id=0)

# 启动POPO
aw.start_app()
aw.sleep(5)

# 检查当前状态
results = aw.ocr_scan_page()
texts = [r['text'] for r in results]

with open("explorer_output/restart_result.txt", "w", encoding="utf-8") as f:
    f.write("OCR texts after restart:\n")
    for t in texts:
        f.write(f"  {t}\n")
    
    # 检查是否在消息列表页
    if any("消息" in t for t in texts):
        f.write("\n状态: 在消息列表页 (已登录)")
    elif any("WorkHub" in t for t in texts):
        f.write("\n状态: 在WorkHub页面")
    elif any("邮箱" in t for t in texts):
        f.write("\n状态: 在登录页面")
    else:
        f.write(f"\n状态: 未知页面")
