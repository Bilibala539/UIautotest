"""
验证 image_ai/ 目录中所有未转正图片的质量
检查项: 文件存在性、尺寸、灰度均值/标准差、红色角标像素
"""
import os
import sys
import cv2
import numpy as np

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

test_path = r"E:\UIAutotest\image_ai"

# image_name_mapping.py 中所有使用 test_path 的图片
test_path_images = [
    "设置页-消息入口.png",
    "消息设置页-页面标题消息.png",
    "消息设置页-开关-开启状态.png",
    "消息设置页-开关-关闭状态.png",
    "聊天页-段落按钮.png",
    "扩展编辑-加粗B按钮.png",
    "扩展编辑-斜体I按钮.png",
    "扩展编辑-下划线U按钮.png",
    "扩展编辑-删除线S按钮.png",
    "扩展编辑-字色A按钮.png",
    "扩展编辑-样式6按钮.png",
    "扩展编辑-Markdown按钮.png",
    "扩展编辑-发送按钮.png",
    "扩展编辑-关闭按钮.png",
    "扩展编辑-样式工具栏.png",
    "长按菜单-收藏按钮.png",
    "长按菜单-收藏文字.png",
    "群设置页-返回箭头.png",
    "群设置页-群头像.png",
    "群设置页-群名称区域.png",
    "群设置页-群成员标题行.png",
    "群设置页-添加成员图标.png",
    "群设置页-移除成员图标.png",
    "群设置页-搜索聊天内容行.png",
    "群设置页-内容筛选标签栏.png",
    "群设置页-群公告行.png",
    "群公告编辑页-空公告输入框占位符.png",
    "群设置页-标签页行.png",
    "群设置页-群管理行.png",
    "通讯录页-左上角通讯录文案.png",
    "通讯录页-搜索按钮.png",
    "通讯录页-添加按钮.png",
    "通讯录页-联系人分组入口.png",
    "通讯录页-群组入口.png",
    "通讯录页-服务号入口.png",
    "通讯录页-字母索引栏.png",
    "通讯录页-底部导航栏消息tab.png",
    "通讯录页-底部导航栏日历tab.png",
    "通讯录页-底部导航栏云空间tab.png",
    "通讯录页-底部导航栏工作台tab.png",
    "通讯录页-底部导航栏易生活tab.png",
    "通讯录页-底部导航栏更多tab.png",
]

print("=" * 120)
print("未转正图片验证报告 (image_ai/)")
print("=" * 120)
print()

passed = []
failed = []
missing = []

for name in test_path_images:
    filepath = os.path.join(test_path, name)
    
    if not os.path.exists(filepath):
        missing.append(name)
        continue
    
    # 使用 numpy 直接读取，绕过 cv2 中文路径问题
    img_data = np.fromfile(filepath, dtype=np.uint8)
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    
    if img is None:
        failed.append((name, "文件损坏/无法读取", "0x0", 0, 0, 0))
        continue
    
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(gray))
    std_val = float(np.std(gray))
    
    # 检测红色角标像素 (R>200, G<160, R-G>40)
    b, g, r = cv2.split(img)
    red_mask = (r > 200) & (g < 160) & ((r.astype(int) - g.astype(int)) > 40)
    red_count = int(np.sum(red_mask))
    
    # 质量检查
    issues = []
    if w < 10 or h < 10:
        issues.append("尺寸过小(<10px)")
    if std_val < 5:
        issues.append("可能空白(std<5)")
    if mean_val < 5:
        issues.append("全黑(mean<5)")
    if mean_val > 250:
        issues.append("全白(mean>250)")
    if red_count > 10:
        issues.append(f"含红色角标({red_count}px)")
    
    record = (name, f"{w}x{h}", mean_val, std_val, red_count, issues)
    if issues:
        failed.append(record)
    else:
        passed.append(record)

# 打印缺失文件
if missing:
    print(f"[文件缺失] 共 {len(missing)} 个图片文件在 image_ai/ 中不存在:")
    print("-" * 80)
    for i, name in enumerate(missing, 1):
        print(f"  {i:2d}. {name}")
    print()

# 打印质量不合格图片
if failed:
    print(f"[质量异常] 共 {len(failed)} 个图片存在质量问题:")
    print("-" * 80)
    for i, record in enumerate(failed, 1):
        name = record[0]
        if len(record) == 6 and isinstance(record[5], list):
            size, mean_v, std_v, red_c, issues = record[1], record[2], record[3], record[4], record[5]
            print(f"  {i:2d}. {name}")
            print(f"      尺寸: {size} | 灰度均值: {mean_v:.1f} | 标准差: {std_v:.1f} | 红色像素: {red_c}")
            print(f"      问题: {'; '.join(issues)}")
        else:
            print(f"  {i:2d}. {name} - {record[1]}")
    print()

# 打印通过的图片
if passed:
    print(f"[质量通过] 共 {len(passed)} 个图片通过基础质量检查:")
    print("-" * 80)
    print(f"  {'#':<3} {'图片名称':<45} {'尺寸':<10} {'均值':<7} {'标准差':<7} {'红色px':<7}")
    print(f"  {'-'*3} {'-'*45} {'-'*10} {'-'*7} {'-'*7} {'-'*7}")
    for i, (name, size, mean_v, std_v, red_c, _) in enumerate(passed, 1):
        print(f"  {i:<3} {name:<45} {size:<10} {mean_v:<7.1f} {std_v:<7.1f} {red_c:<7}")
    print()

# 总结
print("=" * 120)
print(f"总计: {len(test_path_images)} 个未转正图片")
print(f"  - 文件缺失: {len(missing)} 个")
print(f"  - 质量异常: {len(failed)} 个")
print(f"  - 质量通过: {len(passed)} 个")
print()

if not missing and not failed:
    print("所有未转正图片均通过质量检查，可以进行验证测试后转正！")
elif missing:
    print("建议: 缺失的图片需要重新截取 (使用 aw-element 技能)")
if failed:
    print("建议: 质量异常的图片需要按照截取规范重新截取")
print("=" * 120)
