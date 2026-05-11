"""快速验证 enter_workhub AW 方法是否正常工作"""
import sys
sys.path.insert(0, "E:\\UIAutotest")

from utils.aw import create_aw

aw = create_aw(platform="mumu", instance_id=0)

results = []

# 当前页面应该已经在WorkHub了
results.append("=== 检查当前页面状态 ===")
is_workhub = aw.is_on_workhub_home()
results.append(f"当前在WorkHub首页: {is_workhub}")

if is_workhub:
    results.append("已在WorkHub首页，测试基本AW方法...")
    
    # 测试获取模型名称
    model = aw.workhub_get_model_name()
    results.append(f"模型名称: {model}")
    
    # 测试获取技能Tab
    tabs = aw.workhub_get_visible_skill_tabs()
    results.append(f"可见Tab: {tabs}")
    
    results.append("基础AW方法验证通过!")
else:
    results.append("当前不在WorkHub页面，尝试进入...")
    result = aw.enter_workhub()
    results.append(f"进入WorkHub结果: {result}")

with open("explorer_output/test_aw_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
