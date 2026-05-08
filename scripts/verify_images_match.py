"""
验证 image_ai/ 目录中 31 个未转正图片的模板匹配效果
按页面分组逐一验证，记录每个图片的匹配分数
"""
import os
import sys
import time
import logging

sys.path.insert(0, r"E:\UIAutotest")
os.chdir(r"E:\UIAutotest")

# 设置输出编码
sys.stdout.reconfigure(encoding='utf-8')

import cv2
import numpy as np

from utils.devices import ADB_PATH, get_device_port_by_instance
from utils.aw.driver.mumu_driver import MuMuDriver
from utils.aw.aw_base import AWBase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化设备 (强制 ADB 模式，避免 pyautogui failsafe 问题)
instance_id = 0
driver = MuMuDriver(instance_id=instance_id)
driver._adb_mode = True  # 强制 ADB 模式
aw = AWBase(driver)

test_path = r"E:\UIAutotest\image_ai"


def verify_image(image_name: str, threshold: float = 0.8) -> tuple:
    """
    对单张图片进行模板匹配验证

    Args:
        image_name: 图片文件名
        threshold: 匹配阈值

    Returns:
        (bool, float): (是否匹配成功, 最大匹配分数)
    """
    filepath = os.path.join(test_path, image_name)
    if not os.path.exists(filepath):
        return False, 0.0

    template = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), cv2.IMREAD_COLOR)
    if template is None:
        return False, 0.0

    screenshot = aw.take_screenshot()
    if screenshot is None:
        return False, 0.0

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    return max_val >= threshold, float(max_val)


def save_current_screenshot(name: str):
    """保存当前屏幕截图用于调试"""
    save_path = os.path.join(r"E:\UIAutotest\screenshots", f"verify_{name}.png")
    aw.take_screenshot(save_path=save_path)
    return save_path


def adb_cmd(*args):
    """执行 ADB 命令"""
    import subprocess
    serial = driver._device_serial
    cmd = [ADB_PATH, "-s", serial] + list(args)
    result = subprocess.run(cmd, capture_output=True, timeout=30)
    return result.stdout.decode('utf-8', errors='ignore')


def launch_popo():
    """强制重启 POPO 应用并等待消息列表页"""
    # 先 force-stop 再启动，确保从消息列表页开始
    adb_cmd("shell", "am", "force-stop", "com.netease.popo")
    time.sleep(2)
    adb_cmd("shell", "am", "start", "-n", "com.netease.popo/.app.ui.LaunchActivity")
    # 等待应用完全启动
    time.sleep(10)
    # 关闭可能的弹窗
    aw.press_key("escape")
    time.sleep(1)


def navigate_to_message_tab():
    """确保回到消息列表页"""
    from image.image_name_mapping import MESSAGE_TAB_BLUE

    # 先检查是否已经在消息列表页
    pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.65, timeout=2)
    if pos is not None:
        # 点击消息 tab 确保选中
        aw.tap(pos[0], pos[1])
        time.sleep(0.5)
        return

    # 不在，按 back 尝试回退（最多3次，避免退出 POPO）
    for _ in range(3):
        aw.press_key("escape")
        time.sleep(0.5)
        pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.65, timeout=2)
        if pos is not None:
            aw.tap(pos[0], pos[1])
            time.sleep(0.5)
            return

    # 仍然不在，重新启动 POPO
    print("   [导航] 未检测到消息tab，重新启动POPO...")
    launch_popo()
    pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.65, timeout=10)
    if pos is not None:
        aw.tap(pos[0], pos[1])
        time.sleep(0.5)
    else:
        print("   [导航] ⚠️ 仍未检测到消息tab")


def navigate_to_contacts_tab():
    """切换到通讯录/联络 tab"""
    navigate_to_message_tab()
    # 通讯录/联络 tab 在底部导航栏第二个位置 (约 x=155, y=935)
    # 底部导航栏6个tab均分540宽度: 消息(45), 联络(135), 云空间(225), 工作台(315), 易生活(405), 更多(495)
    aw.tap(155, 935)
    time.sleep(2)


def navigate_to_settings():
    """进入设置页"""
    navigate_to_message_tab()
    # 从左侧向右滑出侧边栏
    aw.swipe(10, 480, 400, 480, duration=0.3)
    time.sleep(1)
    # 点击设置
    aw.click_text("设置", timeout=5)
    time.sleep(1)


def navigate_to_msg_settings():
    """进入消息设置页"""
    navigate_to_settings()
    # 点击"消息"入口
    aw.click_text("消息", timeout=5)
    time.sleep(1)


# ==================== 先确保已登录 ====================
print("🔐 确保 POPO 已登录...")
from image.image_name_mapping import MESSAGE_TAB_BLUE

# 启动 POPO
adb_cmd("shell", "input", "keyevent", "3")  # HOME
time.sleep(1)
adb_cmd("shell", "monkey", "-p", "com.netease.popo", "-c", "android.intent.category.LAUNCHER", "1")
time.sleep(10)

# 使用 OCR 检测是否在登录页面
login_check = aw.find_text_by_ocr("登录", timeout=3)
if login_check:
    # 在登录页面，需要执行登录
    print("   检测到登录页面，执行登录流程...")
    from utils.aw.business.mumu import MuMuBusiness
    biz = MuMuBusiness(driver)
    biz.login("grp.popoqa67@corp.netease.com", "Lazermlfy1@")
    time.sleep(5)

# 用高阈值检查是否在消息列表页（ADB 模式下 effective threshold = 0.85-0.05=0.80）
pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.85, timeout=15)
if pos is None:
    # 可能还没到消息列表页，关闭弹窗重试
    aw.press_key("escape")
    time.sleep(1)
    pos = aw.find_image(MESSAGE_TAB_BLUE, threshold=0.85, timeout=10)
    if pos is None:
        print("   ❌ 无法到达消息列表页，保存截图后退出")
        save_current_screenshot("cannot_reach_msg_tab")
        sys.exit(1)

print("   ✅ POPO 已在消息列表页，开始验证")
save_current_screenshot("popo_ready")

# ==================== 开始验证 ====================

results = {}
all_images = []

print()
print("=" * 100)
print("未转正图片模板匹配验证")
print("=" * 100)
print()

# ==================== 第1组: 通讯录页 (13个) ====================
print("📍 [第1组] 导航到: 通讯录页")
navigate_to_contacts_tab()
time.sleep(2)
save_current_screenshot("contacts_page")

contacts_images = [
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

print(f"   验证 {len(contacts_images)} 个图片...")
for name in contacts_images:
    success, score = verify_image(name)
    status = "✅" if success else "❌"
    print(f"   {status} {name:<45} score={score:.3f}")
    results[name] = (success, score)
    all_images.append(name)

# ==================== 第2组: 设置页-消息入口 (1个) ====================
print()
print("📍 [第2组] 导航到: 设置页")
navigate_to_settings()
time.sleep(1)
save_current_screenshot("settings_page")

settings_images = [
    "设置页-消息入口.png",
]

print(f"   验证 {len(settings_images)} 个图片...")
for name in settings_images:
    success, score = verify_image(name)
    status = "✅" if success else "❌"
    print(f"   {status} {name:<45} score={score:.3f}")
    results[name] = (success, score)
    all_images.append(name)

# ==================== 第3组: 消息设置页 (3个) ====================
print()
print("📍 [第3组] 导航到: 消息设置页")
# 点击消息入口进入消息设置页
aw.click_text("消息", timeout=5)
time.sleep(2)
save_current_screenshot("msg_settings_page")

msg_settings_images = [
    "消息设置页-页面标题消息.png",
    "消息设置页-开关-开启状态.png",
    "消息设置页-开关-关闭状态.png",
]

print(f"   验证 {len(msg_settings_images)} 个图片...")
for name in msg_settings_images:
    success, score = verify_image(name)
    status = "✅" if success else "❌"
    print(f"   {status} {name:<45} score={score:.3f}")
    results[name] = (success, score)
    all_images.append(name)

# ==================== 第4组: 聊天页-段落按钮 + 扩展编辑 (11个) ====================
print()
print("📍 [第4组] 导航到: 聊天页 → 扩展编辑工具栏")
navigate_to_message_tab()
time.sleep(1)
# 点击第一个会话进入聊天页
aw.tap(270, 200)
time.sleep(2)
save_current_screenshot("chat_page")

# 先验证段落按钮
chat_para_images = [
    "聊天页-段落按钮.png",
]
print(f"   验证段落按钮...")
for name in chat_para_images:
    success, score = verify_image(name)
    status = "✅" if success else "❌"
    print(f"   {status} {name:<45} score={score:.3f}")
    results[name] = (success, score)
    all_images.append(name)

# 点击段落按钮展开扩展编辑工具栏
print("   点击段落按钮展开扩展编辑...")
from image.image_name_mapping import CHAT_PARAGRAPH_BUTTON
pos = aw.find_image(CHAT_PARAGRAPH_BUTTON, threshold=0.7, timeout=5)
if pos:
    aw.tap(pos[0], pos[1])
    time.sleep(1)
    save_current_screenshot("extended_edit_toolbar")

    extended_images = [
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
    ]
    print(f"   验证 {len(extended_images)} 个扩展编辑图片...")
    for name in extended_images:
        success, score = verify_image(name)
        status = "✅" if success else "❌"
        print(f"   {status} {name:<45} score={score:.3f}")
        results[name] = (success, score)
        all_images.append(name)
else:
    print("   ⚠️ 未找到段落按钮，跳过扩展编辑组图片验证")
    extended_images = [
        "扩展编辑-加粗B按钮.png", "扩展编辑-斜体I按钮.png",
        "扩展编辑-下划线U按钮.png", "扩展编辑-删除线S按钮.png",
        "扩展编辑-字色A按钮.png", "扩展编辑-样式6按钮.png",
        "扩展编辑-Markdown按钮.png", "扩展编辑-发送按钮.png",
        "扩展编辑-关闭按钮.png", "扩展编辑-样式工具栏.png",
    ]
    for name in extended_images:
        results[name] = (False, 0.0)
        all_images.append(name)
        print(f"   ❌ {name:<45} score=0.000 (页面未到达)")

# ==================== 第5组: 长按菜单 (2个) ====================
print()
print("📍 [第5组] 触发: 长按消息展示菜单")
# 关闭扩展编辑（按 back）
aw.press_key("escape")
time.sleep(1)
# 长按消息区域 (大约聊天消息位置)
aw.driver.long_press(270, 400, duration=1.0)
time.sleep(1)
save_current_screenshot("long_press_menu")

longpress_images = [
    "长按菜单-收藏按钮.png",
    "长按菜单-收藏文字.png",
]

print(f"   验证 {len(longpress_images)} 个图片...")
for name in longpress_images:
    success, score = verify_image(name)
    status = "✅" if success else "❌"
    print(f"   {status} {name:<45} score={score:.3f}")
    results[name] = (success, score)
    all_images.append(name)

# ==================== 第6组: 群公告编辑页 (1个) ====================
print()
print("📍 [第6组] 群公告编辑页 — 需要特殊导航，单独验证")
# 此图片需要进入群设置 → 群公告，操作路径较长
# 先检查图片本身质量是否有问题（已在之前通过质量检查）
# 这里我们简单在当前页面尝试匹配
group_images = [
    "群公告编辑页-空公告输入框占位符.png",
]
print(f"   注: 群公告编辑页需要完整操作路径到达，当前仅做图片存在性确认")
for name in group_images:
    filepath = os.path.join(test_path, name)
    exists = os.path.exists(filepath)
    status = "📦" if exists else "❌"
    print(f"   {status} {name:<45} (文件存在={exists}, 需单独验证)")
    results[name] = (None, -1)  # None 表示未验证
    all_images.append(name)

# ==================== 总结 ====================
print()
print("=" * 100)
print("📊 验证结果总结")
print("=" * 100)

passed = [(k, v) for k, v in results.items() if v[0] is True]
failed = [(k, v) for k, v in results.items() if v[0] is False]
skipped = [(k, v) for k, v in results.items() if v[0] is None]

print(f"  ✅ 匹配成功: {len(passed)} 个")
print(f"  ❌ 匹配失败: {len(failed)} 个")
print(f"  ⏭️  未验证: {len(skipped)} 个")
print()

if failed:
    print("❌ 失败详情:")
    print("-" * 80)
    for name, (_, score) in failed:
        print(f"  {name:<50} max_score={score:.3f}")
    print()

if passed:
    print("✅ 通过详情:")
    print("-" * 80)
    for name, (_, score) in passed:
        print(f"  {name:<50} max_score={score:.3f}")

print()
print("=" * 100)
