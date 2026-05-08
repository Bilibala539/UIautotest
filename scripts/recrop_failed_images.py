"""
从设备实时截图中重新裁切所有验证失败的图片
按页面分组导航 + 裁切
"""
import os
import sys
import time
import subprocess

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")
sys.stdout.reconfigure(encoding='utf-8')

import cv2
import numpy as np

from utils.devices import ADB_PATH, get_device_port_by_instance
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.aw_base import AWBase

# 初始化
instance_id = 0
driver = MuMuDriver(instance_id=instance_id)
driver._adb_mode = True
aw = AWBase(driver)

test_path = r"E:\UIAutotest\image_ai"
serial = driver._device_serial


def adb(*args):
    cmd = [ADB_PATH, "-s", serial] + list(args)
    return subprocess.run(cmd, capture_output=True, timeout=30).stdout


def take_screenshot_cv() -> np.ndarray:
    """直接通过 ADB 截取屏幕，返回 cv2 格式图像"""
    raw = adb("exec-out", "screencap", "-p")
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    return img


def save_element(img: np.ndarray, x1: int, y1: int, x2: int, y2: int, filename: str) -> bool:
    """
    从截图中裁切元素并保存到 image_ai 目录

    Args:
        img: 原始截图 (BGR)
        x1, y1, x2, y2: 裁切坐标
        filename: 保存的文件名

    Returns:
        bool: 是否保存成功
    """
    h, w = img.shape[:2]

    # 前置检查
    assert x1 < x2, f"x1({x1}) >= x2({x2})"
    assert y1 < y2, f"y1({y1}) >= y2({y2})"
    assert x1 >= 0 and y1 >= 0, f"坐标为负数: ({x1},{y1})"
    assert x2 <= w and y2 <= h, f"坐标超出范围: ({x2},{y2}) > ({w},{h})"
    assert x2 - x1 >= 10, f"宽度太小: {x2-x1}px"
    assert y2 - y1 >= 10, f"高度太小: {y2-y1}px"

    cropped = img[y1:y2, x1:x2]

    # 质量检查
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    assert np.std(gray) > 5, f"图片可能为空白 (std={np.std(gray):.1f})"
    assert 5 < np.mean(gray) < 250, f"图片全黑/全白 (mean={np.mean(gray):.1f})"

    # 红色角标检查
    b, g, r = cropped[:, :, 0].astype(int), cropped[:, :, 1].astype(int), cropped[:, :, 2].astype(int)
    red_mask = (r > 200) & (g < 160) & (b < 170) & (r - g > 40)
    red_count = red_mask.sum()
    if red_count > 0:
        print(f"    ⚠️ 检测到 {red_count} 个红色角标像素，请确认！")

    filepath = os.path.join(test_path, filename)
    cv2.imencode('.png', cropped)[1].tofile(filepath)
    print(f"    ✅ 已保存: {filename} ({x2-x1}x{y2-y1}px)")
    return True


def find_dark_text_bounds(img: np.ndarray, region: tuple, threshold: int = 100) -> tuple:
    """
    在指定区域找到深色文字/图标的边界

    Args:
        img: 原始截图
        region: (x1, y1, x2, y2) 搜索区域
        threshold: 灰度阈值

    Returns:
        (x1, y1, x2, y2): 紧贴的边界坐标 (绝对坐标)
    """
    rx1, ry1, rx2, ry2 = region
    crop = img[ry1:ry2, rx1:rx2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    dark = np.where(gray < threshold)
    if len(dark[0]) == 0:
        return None
    y_min, y_max = dark[0].min(), dark[0].max()
    x_min, x_max = dark[1].min(), dark[1].max()
    # 加 1-2px padding
    return (rx1 + x_min - 1, ry1 + y_min - 1, rx1 + x_max + 2, ry1 + y_max + 2)


def find_colored_element_bounds(img: np.ndarray, region: tuple, min_sat: int = 60) -> tuple:
    """在指定区域找到彩色元素的边界"""
    rx1, ry1, rx2, ry2 = region
    crop = img[ry1:ry2, rx1:rx2]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask = hsv[:, :, 1] > min_sat
    coords = np.where(mask)
    if len(coords[0]) == 0:
        return None
    y_min, y_max = coords[0].min(), coords[0].max()
    x_min, x_max = coords[1].min(), coords[1].max()
    return (rx1 + x_min - 1, ry1 + y_min - 1, rx1 + x_max + 2, ry1 + y_max + 2)


# ==================== 辅助函数 ====================
from image.image_name_mapping import MESSAGE_TAB_BLUE


def go_home():
    """回到消息列表页"""
    pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.65, timeout=2)
    if pos:
        aw.tap(pos[0], pos[1])
        time.sleep(0.5)
        return
    # 按 back 几次
    for _ in range(5):
        aw.press_key("escape")
        time.sleep(0.5)
        pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.65, timeout=1)
        if pos:
            aw.tap(pos[0], pos[1])
            time.sleep(0.5)
            return
    # 重启 POPO
    adb("shell", "am", "force-stop", "com.netease.popo")
    time.sleep(2)
    adb("shell", "am", "start", "-n", "com.netease.popo/.app.ui.LaunchActivity")
    time.sleep(10)


# ==================== 开始操作 ====================
print("=" * 80)
print("🔧 从设备实时截图中重新裁切失败的元素图片")
print("=" * 80)
print()

# ==================== 第1组: 通讯录页 ====================
print("📍 [第1组] 导航到通讯录页...")
go_home()
time.sleep(1)
# 点击底部第二个 tab (联络/通讯录)
aw.tap(155, 935)
time.sleep(2)

# 截取当前页面
contacts_img = take_screenshot_cv()
cv2.imencode('.png', contacts_img)[1].tofile("screenshots/recrop_contacts.png")
print(f"  截图尺寸: {contacts_img.shape}")
print()

# 1.1 通讯录页-左上角通讯录文案
print("  裁切: 通讯录页-左上角通讯录文案.png")
# 标题 "通讯录" 在搜索栏左上方, 根据分析在 y=35-55, x=10-100 区域
# 但我们的分析显示暗色文字在 y=50-55, x=38-57 —— 这似乎太小了
# 让我们先找到搜索栏上方的文字区域
bounds = find_dark_text_bounds(contacts_img, (10, 35, 200, 55), threshold=120)
if bounds:
    save_element(contacts_img, *bounds, "通讯录页-左上角通讯录文案.png")
else:
    # 如果标题不在这个区域，尝试更大范围
    print("    ⚠️ 未找到标题文字，尝试扩大范围")
    bounds = find_dark_text_bounds(contacts_img, (5, 30, 250, 60), threshold=150)
    if bounds:
        save_element(contacts_img, *bounds, "通讯录页-左上角通讯录文案.png")
    else:
        print("    ❌ 无法定位标题文字")

# 1.2 通讯录页-搜索按钮
print("  裁切: 通讯录页-搜索按钮.png")
# 搜索图标在搜索栏左侧，大约 y=55-90, x=25-65
# 从之前分析：y=50, x=38-57 有暗色像素，y=87-90 x=39-46 也有
# 搜索栏区域：y=55-90, 整个区域是灰色背景
# 搜索按钮（放大镜图标）通常在搜索栏最左边
bounds = find_dark_text_bounds(contacts_img, (25, 45, 70, 100), threshold=120)
if bounds:
    save_element(contacts_img, *bounds, "通讯录页-搜索按钮.png")
else:
    print("    ❌ 无法定位搜索按钮")

# 1.3 通讯录页-添加按钮
print("  裁切: 通讯录页-添加按钮.png")
# '+' 按钮在右上角, 分析显示 y=58-74, x=484-509
bounds = find_dark_text_bounds(contacts_img, (475, 45, 525, 80), threshold=120)
if bounds:
    save_element(contacts_img, *bounds, "通讯录页-添加按钮.png")
else:
    print("    ❌ 无法定位添加按钮")

# 1.4-1.6 列表入口（联系人分组、群组、服务号）
# 这些通常是带彩色图标 + 文字的列表项
# 从分析看：
# - 彩色图标在 x=66-99, y=160-310 区域
# - y=130-160: 第一个列表项（"联系人分组"）
# - 分隔线在 y=309-313
# 需要找到各项的具体 y 范围

print("  裁切: 通讯录页-联系人分组入口.png")
# 联系人分组：图标+文字，大约 y=120-175
# 从像素分析: y=130-160 有内容, x=25-455
# 包含整行（图标+文字）
item1_y_start = 115
item1_y_end = 170
item1_bounds = find_dark_text_bounds(contacts_img, (15, item1_y_start, 460, item1_y_end), threshold=150)
if item1_bounds:
    # 确保包含彩色图标
    color_bounds = find_colored_element_bounds(contacts_img, (15, item1_y_start, 460, item1_y_end))
    if color_bounds:
        # 合并文字和图标的边界
        x1 = min(item1_bounds[0], color_bounds[0])
        y1 = min(item1_bounds[1], color_bounds[1])
        x2 = max(item1_bounds[2], color_bounds[2])
        y2 = max(item1_bounds[3], color_bounds[3])
        save_element(contacts_img, x1, y1, x2, y2, "通讯录页-联系人分组入口.png")
    else:
        save_element(contacts_img, *item1_bounds, "通讯录页-联系人分组入口.png")
else:
    print("    ❌ 无法定位联系人分组入口")

print("  裁切: 通讯录页-群组入口.png")
# 群组：大约在分隔线下方，y=175-260
item2_bounds = find_dark_text_bounds(contacts_img, (15, 170, 460, 265), threshold=150)
if item2_bounds:
    color_bounds = find_colored_element_bounds(contacts_img, (15, 170, 460, 265))
    if color_bounds:
        x1 = min(item2_bounds[0], color_bounds[0])
        y1 = min(item2_bounds[1], color_bounds[1])
        x2 = max(item2_bounds[2], color_bounds[2])
        y2 = max(item2_bounds[3], color_bounds[3])
        save_element(contacts_img, x1, y1, x2, y2, "通讯录页-群组入口.png")
    else:
        save_element(contacts_img, *item2_bounds, "通讯录页-群组入口.png")
else:
    print("    ❌ 无法定位群组入口")

print("  裁切: 通讯录页-服务号入口.png")
# 服务号：大约 y=265-320
item3_bounds = find_dark_text_bounds(contacts_img, (15, 265, 460, 330), threshold=150)
if item3_bounds:
    color_bounds = find_colored_element_bounds(contacts_img, (15, 265, 460, 330))
    if color_bounds:
        x1 = min(item3_bounds[0], color_bounds[0])
        y1 = min(item3_bounds[1], color_bounds[1])
        x2 = max(item3_bounds[2], color_bounds[2])
        y2 = max(item3_bounds[3], color_bounds[3])
        save_element(contacts_img, x1, y1, x2, y2, "通讯录页-服务号入口.png")
    else:
        save_element(contacts_img, *item3_bounds, "通讯录页-服务号入口.png")
else:
    print("    ❌ 无法定位服务号入口")

# 1.7 字母索引栏
print("  裁切: 通讯录页-字母索引栏.png")
# 字母索引在右侧, x=500-540, 从分析看 y=760-800 有暗色内容
# 但字母索引通常更长，覆盖整个列表区域
# 找到右侧边缘的所有暗色内容
right_strip = contacts_img[:, 495:540]
gray_strip = cv2.cvtColor(right_strip, cv2.COLOR_BGR2GRAY)
dark_rows = np.where(gray_strip < 150)
if len(dark_rows[0]) > 0:
    y_start = dark_rows[0].min()
    y_end = dark_rows[0].max()
    x_start = 495 + dark_rows[1].min()
    x_end = 495 + dark_rows[1].max()
    if y_end - y_start > 30:  # 索引栏应该较长
        save_element(contacts_img, x_start - 1, y_start - 1, x_end + 2, y_end + 2, "通讯录页-字母索引栏.png")
    else:
        print(f"    ⚠️ 右侧内容太短({y_end-y_start}px)，可能不是索引栏")
else:
    print("    ❌ 无法定位字母索引栏")

# 1.8-1.13 底部导航栏 tabs
# 从分析: 6个tab, x范围: [0-90, 90-180, 180-270, 270-360, 360-450, 450-540]
# 安全截取区域: y=860-932
nav_tabs = [
    # (tab_name, x_start, x_end)
    ("通讯录页-底部导航栏日历tab.png", 90, 180),  # 第2个tab - 但这是"联络"tab，当前选中(蓝色)
    ("通讯录页-底部导航栏更多tab.png", 450, 540),
]

print()
print("  裁切底部导航栏 tabs...")
# 重新分析：从之前分析看
# Tab[0] 消息: x=[30,80], y=[863,930] (绝对)
# Tab[1] 联络: x=[120,149], y=[874,930] (蓝色)
# Tab[2] 云空间: x=[204,245], y=[878,930]
# Tab[3] 工作台: x=[294,335], y=[878,929]
# Tab[4] 易生活: x=[384,426], y=[876,930]
# Tab[5] 更多: x=[480,509], y=[877,930]

# 通讯录页-底部导航栏日历tab -- 这个名字有误？可能是"联络"tab
# 让我检查原始名字：是"日历tab"，但当前POPO版本可能没有日历tab
# 它在消息和云空间之间，实际是"联络"tab
# 那"日历tab"对应的可能是旧版本的。先裁切当前实际的

# 底部导航栏日历tab: 在当前POPO中可能不存在。先从截图的实际内容裁切
# 分析当前 tab 位置：
print("  裁切: 通讯录页-底部导航栏日历tab.png (第2个tab-联络)")
# 第2个tab 的范围大约 x=90-180, y=860-932
nav_crop = contacts_img[860:932, 90:180]
gray_nav = cv2.cvtColor(nav_crop, cv2.COLOR_BGR2GRAY)
dark_nav = np.where(gray_nav < 200)
if len(dark_nav[0]) > 0:
    y1_n = 860 + dark_nav[0].min() - 1
    y2_n = 860 + dark_nav[0].max() + 2
    x1_n = 90 + dark_nav[1].min() - 1
    x2_n = 90 + dark_nav[1].max() + 2
    save_element(contacts_img, x1_n, y1_n, x2_n, y2_n, "通讯录页-底部导航栏日历tab.png")
else:
    print("    ❌ 无法定位日历tab")

print("  裁切: 通讯录页-底部导航栏更多tab.png (第6个tab)")
nav_crop6 = contacts_img[860:932, 450:540]
gray_nav6 = cv2.cvtColor(nav_crop6, cv2.COLOR_BGR2GRAY)
dark_nav6 = np.where(gray_nav6 < 200)
if len(dark_nav6[0]) > 0:
    y1_n = 860 + dark_nav6[0].min() - 1
    y2_n = 860 + dark_nav6[0].max() + 2
    x1_n = 450 + dark_nav6[1].min() - 1
    x2_n = 450 + dark_nav6[1].max() + 2
    save_element(contacts_img, x1_n, y1_n, x2_n, y2_n, "通讯录页-底部导航栏更多tab.png")
else:
    print("    ❌ 无法定位更多tab")

# ==================== 第2组: 聊天页 - 段落按钮 + 扩展编辑 ====================
print()
print("📍 [第2组] 导航到聊天页...")
go_home()
time.sleep(1)
# 点击第一个会话
aw.tap(270, 200)
time.sleep(2)

chat_img = take_screenshot_cv()
cv2.imencode('.png', chat_img)[1].tofile("screenshots/recrop_chat.png")
print(f"  截图尺寸: {chat_img.shape}")

# 段落按钮通常在输入框右侧或工具栏中
# 让我分析输入区域（通常在底部）
print("  分析聊天页底部工具栏...")
# 输入框区域通常在 y=880-960 或者更上面一些
# 检查 y=850-950 区域的内容
bottom_area = chat_img[830:950, :]
gray_bot = cv2.cvtColor(bottom_area, cv2.COLOR_BGR2GRAY)
for y in range(0, 120, 5):
    row = gray_bot[y, :]
    dark = np.where(row < 150)[0]
    if len(dark) > 3:
        print(f"    y={830+y}: dark_count={len(dark)}, x=[{dark[0]},{dark[-1]}]")

# 点击输入框区域以激活键盘
print()
print("  点击输入框区域激活键盘...")
aw.tap(270, 900)
time.sleep(1)

chat_img2 = take_screenshot_cv()
cv2.imencode('.png', chat_img2)[1].tofile("screenshots/recrop_chat_keyboard.png")

# 分析键盘弹出后的工具栏位置
print("  分析键盘弹出后的工具栏...")
# 当键盘弹出时，输入框和工具栏会上移
# 段落按钮(¶)通常在输入框上方的工具栏中
# 扫描中间区域找到工具栏
mid_area = chat_img2[400:700, :]
gray_mid = cv2.cvtColor(mid_area, cv2.COLOR_BGR2GRAY)
for y in range(0, 300, 5):
    row = gray_mid[y, :]
    dark = np.where(row < 100)[0]
    if len(dark) > 3:
        print(f"    y={400+y}: dark_count={len(dark)}, x=[{dark[0]},{dark[-1]}]")

print()
print("  完成第2组分析。需要查看截图确定具体位置。")

# ==================== 第3组: 长按菜单 ====================
print()
print("📍 [第3组] 触发长按菜单...")
# 先关闭键盘
aw.press_key("escape")
time.sleep(0.5)
# 长按一条消息
aw.driver.long_press(270, 400, duration=1.5)
time.sleep(1)

longpress_img = take_screenshot_cv()
cv2.imencode('.png', longpress_img)[1].tofile("screenshots/recrop_longpress.png")
print(f"  截图尺寸: {longpress_img.shape}")

# 分析长按菜单中的"收藏"按钮位置
print("  分析长按菜单...")
# 长按菜单通常是一个浮层，包含复制、转发、收藏等选项
# 扫描整个图片找到菜单区域
gray_lp = cv2.cvtColor(longpress_img, cv2.COLOR_BGR2GRAY)
for y in range(0, 960, 10):
    row = gray_lp[y, :]
    dark = np.where(row < 100)[0]
    if len(dark) > 10:
        print(f"    y={y}: dark_count={len(dark)}, x=[{dark[0]},{dark[-1]}]")

print()
print("=" * 80)
print("📊 裁切完成！请检查 screenshots/ 目录下的 recrop_* 截图确认页面状态")
print("=" * 80)
