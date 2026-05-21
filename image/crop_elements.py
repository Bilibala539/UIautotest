"""
元素截取脚本 - 从消息页面截图中截取UI元素
"""
from PIL import Image
import os

path = r"E:\UIAutotest\image"
source_img = os.path.join(path, "POPO-screenshot-20260311-205115.png")

# 读取原始截图
img = Image.open(source_img)
print(f"原始图片尺寸: {img.size}")

# 定义需要截取的元素及其坐标 (left, upper, right, lower)
# 截取原则：
# 1. 避免截取动态元素（如消息红点、未读数量等）
# 2. 只截取静态、稳定的元素部分
# 3. 排除相邻元素的干扰
elements = [
    # 底部导航栏元素
    # 注意：消息图标截取图标主体+文字，收紧右上边界避开红点99+
    {"name": "消息tab页-底部导航栏-消息图标蓝色.png", "area": (30, 878, 80, 930)},
    {"name": "消息tab页-底部导航栏-工作台图标.png", "area": (230, 860, 310, 930)},
    {"name": "消息tab页-底部导航栏-通讯录图标.png", "area": (330, 860, 410, 930)},
    {"name": "消息tab页-底部导航栏-更多图标.png", "area": (435, 860, 515, 930)},
    
    # 顶部操作按钮
    {"name": "消息tab页-顶部搜索按钮.png", "area": (400, 95, 450, 135)},
    {"name": "消息tab页-顶部添加按钮.png", "area": (460, 95, 510, 135)},
    
    # 快捷联系人栏
    {"name": "消息tab页-展开按钮.png", "area": (450, 165, 510, 245)},
    
    # 消息标题 - 只截取"消息"文字，排除左侧头像元素
    {"name": "消息tab页-顶部消息标题.png", "area": (85, 95, 160, 135)},
]

# 批量截取并保存
print("\n开始截取元素...")
for elem in elements:
    try:
        cropped = img.crop(elem["area"])
        save_path = os.path.join(path, elem["name"])
        cropped.save(save_path)
        print(f"[OK] 已保存: {elem['name']}")
    except Exception as e:
        print(f"[FAIL] 截取失败 {elem['name']}: {e}")

print("\n[DONE] 所有元素截取完成!")
