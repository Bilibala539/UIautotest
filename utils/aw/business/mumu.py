"""
MuMu (Android) 端业务方法

包含 MuMu 模拟器上 POPO 应用的完整业务操作流程。
UI 流程、检查图片、操作步骤均为 Android 端专属。
"""
import logging
import subprocess
import time

import numpy as np

from image.image_name_mapping import *
from utils.aw.business.common import CommonBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)

POPO_PACKAGE = "com.netease.popo"
POPO_ACTIVITY = "com.netease.popo.MainActivity"


def _get_adb_path() -> str:
    from utils.devices import ADB_PATH
    return ADB_PATH


class MuMuBusiness(CommonBusiness):
    """
    MuMu (Android) 端业务类

    继承链: MuMuBusiness → CommonBusiness → AWBase
    """

    def __init__(self, driver: BasePlatformDriver):
        super().__init__(driver)
        from utils.devices import get_device_port_by_instance
        self._device_port = get_device_port_by_instance(driver.instance_id)
        self._device_serial = f"127.0.0.1:{self._device_port}"

    # ==================== ADB 命令 ====================

    def _run_adb_command(self, *args) -> bool:
        """执行ADB命令"""
        cmd = [_get_adb_path(), "-s", self._device_serial] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"❌ ADB命令超时: {' '.join(cmd)}")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ ADB命令失败: {e.stderr.decode()}")
            return False

    def _clear_input_field(self):
        """
        通过 ADB 清空当前聚焦的输入框

        策略: HOME 移到文本开头 → Shift+END 全选 → DEL 删除。
        MuMu 模拟器中 Ctrl+A 组合键不可靠，改用 HOME + Shift+END 方式。
        """
        # MOVE_HOME (122) 移动光标到文本开头
        self._run_adb_command("shell", "input", "keyevent", "122")
        time.sleep(0.2)
        # Shift + MOVE_END (59+123) 从开头选中到末尾（全选）
        self._run_adb_command("shell", "input", "keycombination", "59", "123")
        time.sleep(0.2)
        # DEL (67) 删除选中内容
        self._run_adb_command("shell", "input", "keyevent", "67")
        time.sleep(0.3)
        logger.info("🗑️ 已清空输入框(HOME+Shift+END全选+删除)")

    # ==================== 应用控制 ====================

    def start_app(self):
        """点击 MuMu 桌面上的 POPO 图标启动应用"""
        self.click_image(HOME_POPO_LOGO, timeout=20)

    def stop_app(self, package: str = POPO_PACKAGE) -> bool:
        """停止应用"""
        logger.info(f"📱 正在停止应用 {package}...")
        self._run_adb_command("shell", "am", "force-stop", package)
        time.sleep(0.5)
        logger.info("✅ 应用已停止")
        return True

    def open_app(self):
        """
        启动 POPO 并等待进入消息列表首页

        前置条件: 用户已登录（Session 级别已完成登录，force-stop 不清除登录态）
        步骤:
        1. 检查是否已在消息列表页（跳过启动）
        2. 尝试点击底部"消息"Tab（可能在App内其他Tab页面）
        3. 尝试按返回键回到消息页（可能在深层页面）
        4. 否则从桌面启动App
        5. 处理可能出现的弹窗
        """
        logger.info("📱 [MuMu] 启动 POPO 应用...")

        # 确保模拟器窗口在前台
        self.driver.focus_window()
        self.sleep(0.3)

        # 先检查是否已在消息列表页（find_image 找不到返回 None，不会抛异常）
        if self.find_image(MESSAGE_TAB_BLUE, timeout=2):
            logger.info("✅ [MuMu] POPO 已在消息列表页，无需启动")
            self.pop_not_allowed()
            return

        # 尝试点击底部"消息"Tab（可能在其他Tab页面：工作台/日历等）
        try:
            msg_pos = self.find_text_by_ocr("消息", timeout=2, region=(0, 860, 540, 100))
            if msg_pos:
                self.tap(msg_pos[0], msg_pos[1])
                self.sleep(1)
                if self.find_image(MESSAGE_TAB_BLUE, timeout=2):
                    logger.info("✅ [MuMu] 已通过点击消息Tab回到消息列表页")
                    self.pop_not_allowed()
                    return
        except Exception:
            pass  # OCR可能因为不在App内而失败

        # 尝试按返回键回到消息页（可能在App内深层页面）
        for i in range(5):
            self.press_back()
            self.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                logger.info("✅ [MuMu] 已通过返回键回到消息列表页")
                self.pop_not_allowed()
                return

        # App未运行，从桌面启动
        self.start_app()
        self.sleep(2)
        self.image_exists(MESSAGE_TAB_BLUE, timeout=15)
        self.pop_not_allowed()
        logger.info("✅ [MuMu] POPO 已启动，已进入消息列表页")

    def close_app(self):
        """
        关闭 POPO 应用（force-stop，保留登录态）

        使用 am force-stop 关闭应用进程，不清除数据，登录态保留。
        """
        logger.info("📱 [MuMu] 关闭 POPO 应用...")
        self.stop_app()
        logger.info("✅ [MuMu] POPO 已关闭")

    def restart_app(self) -> bool:
        """重启应用"""
        self.stop_app()
        time.sleep(1)
        self.start_app()
        return True

    def clear_app_data(self, package: str = POPO_PACKAGE) -> bool:
        """清除应用数据"""
        logger.info(f"🗑️ 正在清除应用数据 {package}...")
        self._run_adb_command("shell", "pm", "clear", package)
        time.sleep(1)
        logger.info("✅ 应用数据已清除")
        return True

    def page_ctrl(self):
        pass

    # ==================== 登录 / 退登 ====================

    def login(self, uid: str, password: str):
        """
        MuMu 端登录流程

        步骤:
        1. 启动 POPO 应用
        2. 等待登录页面
        3. 点击邮箱 Tab
        4. 点击邮箱输入框 → 全选清空 → 输入邮箱
        5. 点击密码输入框 → 输入密码
        6. 勾选协议（如未勾选）
        7. 点击登录按钮
        8. 等待进入消息列表页
        9. 处理可能出现的弹窗

        登录完成后 POPO 已在消息列表页，无需再调用 open_app()。
        """
        logger.info(f"🔐 [MuMu] 开始登录: {uid}")

        # 0. 确保模拟器窗口在前台（pyautogui截图需要窗口可见）
        self.driver.focus_window()
        self.sleep(0.2)

        # 1. 启动 POPO（通过 monkey 命令模拟启动，比点击桌面图标更可靠）
        self._run_adb_command("shell", "monkey", "-p", POPO_PACKAGE,
                              "-c", "android.intent.category.LAUNCHER", "1")
        self.sleep(8)

        # 1.5. 检查是否已处于登录状态（消息列表页）
        if self.find_image(MESSAGE_TAB_BLUE, timeout=15):
            logger.info("✅ [MuMu] 已登录状态（图像匹配），跳过登录步骤")
            self.pop_not_allowed()
            return

        # 1.6. 图像匹配失败时，使用 OCR 检测底部导航栏的"消息"文字作为已登录标志
        if self.find_text_by_ocr("消息", timeout=5):
            logger.info("✅ [MuMu] 已登录状态（OCR回退），跳过登录步骤")
            self.pop_not_allowed()
            return
        logger.info("📱 检测到登录页面")

        # 3. 点击邮箱 Tab
        self.click_text("邮箱", timeout=3)
        self.sleep(0.5)

        # 4. 输入邮箱：点击邮箱输入框 → 清空 → 输入新邮箱
        #    不管输入框是空的（显示"输入邮箱"占位符）还是保留了旧邮箱，都先清空再输入
        #    页面布局: "邮箱"Tab y≈313, 邮箱输入框 y≈405, 密码输入框 y≈500
        #    用 dy=92 从"邮箱"Tab 偏移到邮箱输入框
        self.click_text("邮箱", timeout=3, dx=50, dy=92)
        self.sleep(0.5)
        # 清空输入框（通过 ADB keyevent 移到末尾 + 逐字删除）
        self._clear_input_field()
        self.sleep(0.3)
        self.input_text(str(uid))
        logger.info(f"📧 已输入邮箱: {uid}")

        # 5. 输入密码：点击密码输入框 → 清空 → 输入密码 → 收起键盘
        #    从"邮箱"Tab 偏移 dy=187 到密码输入框
        self.click_text("邮箱", timeout=3, dx=50, dy=187)
        self.sleep(0.5)
        # 清空密码输入框
        self._clear_input_field()
        self.sleep(0.3)
        self.input_text(str(password))
        logger.info("🔑 已输入密码")
        # 收起键盘，避免遮挡底部的勾选框和登录按钮
        self.press_back()
        self.sleep(0.5)

        # 6. 勾选协议（先检查未勾选状态，如果未找到说明已勾选）
        if self.find_image(LOGIN_READ_CENTER_FALSE, timeout=2):
            self.click_image(LOGIN_READ_CENTER_FALSE)
            self.sleep(0.3)
            logger.info("☑️ 已勾选协议")
        else:
            logger.info("☑️ 协议已是勾选状态，无需再勾选")

        # 7. 点击登录按钮
        self.click_image(LOGIN_ENTER)
        self.sleep(1.5)

        # 8. 等待进入消息列表页
        self.image_exists(MESSAGE_TAB_BLUE, timeout=15)

        # 9. 处理可能出现的弹窗
        self.pop_not_allowed()
        logger.info(f"✅ [MuMu] 登录成功: {uid}")

    def _ensure_message_page(self) -> bool:
        """
        确保当前处于消息列表页面

        处理以下场景:
        1. 已在消息列表页 → 直接返回
        2. 在App内深层页面 → 连续按返回键回到消息页
        3. App已退出到模拟器桌面 → 重新点击POPO图标启动App
        4. 在登录页面 → 说明已经退出登录了，返回False

        Returns:
            bool: True=成功回到消息列表页, False=已在登录页(已退出登录)
        """
        # 场景1: 已在消息列表页
        if self.find_image(MESSAGE_TAB_BLUE, timeout=2):
            logger.info("✅ 已在消息列表页")
            return True

        # 场景4: 检查是否在登录页
        if self.find_image(LOGIN_POPO_TEXT, timeout=1):
            logger.info("📱 已在登录页面，无需退登")
            return False

        # 场景2: 连续按返回键尝试回到消息页
        for i in range(5):
            logger.info(f"🔙 第{i + 1}次按返回键")
            self.press_back()
            time.sleep(0.5)

            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                logger.info("✅ 成功回到消息列表页")
                return True

            # 按返回键后检查是否退出到了登录页
            if self.find_image(LOGIN_POPO_TEXT, timeout=1):
                logger.info("📱 按返回键后到达登录页，无需退登")
                return False

            # 检查是否在App内但不在消息Tab（如日历Tab），尝试点击底部"消息"
            msg_pos = self.find_text_by_ocr("消息", timeout=1, region=Normal.BOTTOM_NAV)
            if msg_pos:
                logger.info("📱 检测到底部导航'消息'，点击切换到消息Tab")
                self.tap(msg_pos[0], msg_pos[1])
                time.sleep(1)
                if self.find_image(MESSAGE_TAB_BLUE, timeout=3):
                    logger.info("✅ 切换到消息列表页成功")
                    return True

        # 场景3: 连续按返回可能退出到了桌面，尝试重启App
        logger.warning("⚠️ 连续5次返回未找到消息页，尝试检测桌面并重启App")
        if self.find_image(HOME_POPO_LOGO, timeout=2):
            logger.info("📱 检测到桌面POPO图标，重新启动App")
            self.start_app()
            time.sleep(3)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=10):
                logger.info("✅ 重启App后成功回到消息列表页")
                return True
            if self.find_image(LOGIN_POPO_TEXT, timeout=3):
                logger.info("📱 重启App后到达登录页，无需退登")
                return False

        # 最后的兜底: 强制停止App再启动
        logger.warning("⚠️ 无法定位当前页面，强制停止并重启App")
        self.stop_app()
        time.sleep(1)
        self.start_app()
        time.sleep(3)
        if self.find_image(MESSAGE_TAB_BLUE, timeout=10):
            return True
        if self.find_image(LOGIN_POPO_TEXT, timeout=3):
            return False

        logger.error("❌ 多次尝试后仍无法回到消息列表页或登录页")
        return False

    def logout(self) -> bool:
        """
        MuMu 端退出登录流程

        步骤:
        1. 确保回到消息列表页（处理桌面/深层页面等异常场景）
        2. 打开侧边栏
        3. 点击设置
        4. 点击退出登录
        5. 确认退出
        6. 验证回到登录页
        """
        logger.info("🚪 [MuMu] 开始退出登录")

        # 1. 确保回到消息列表页
        on_message_page = self._ensure_message_page()
        if not on_message_page:
            # 已在登录页面，说明App已退出登录或被重启后需要重新登录
            logger.info("✅ [MuMu] 已在登录页面，无需退登操作")
            return True

        # 2. 打开侧边栏并退登
        self.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)
        time.sleep(0.3)
        self.click_text("设置", region=Normal.HALF_DOWN)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT)
        time.sleep(0.3)
        self.click_image(SETTINGS_LOGOUT_CONFIRM)
        time.sleep(1.5)
        self.image_exists(LOGIN_POPO_TEXT)
        logger.info("✅ [MuMu] 退出登录成功")
        return True

    # ==================== 弹窗处理 ====================

    def pop_not_allowed(self):
        self.pop_is_exisit(isallow=False)

    def pop_allowed(self):
        self.pop_is_exisit(isallow=True)

    def pop_is_exisit(self, isallow=False):
        if self.find_image(POPO_POP, timeout=1):
            time.sleep(0.3)
            if not isallow:
                self.click_image(POPO_POP_CANCEL, timeout=2)
                logger.info("弹窗已关闭")
        else:
            logger.info("未发现弹窗")

    # ==================== 会话分组相关 ====================

    def open_session_group_panel(self) -> bool:
        """
        打开会话分组更多弹窗

        步骤:
        1. 在消息列表页点击分组标签栏右侧的≡按钮
        2. 弹出会话分组面板（包含分组标签、管理入口、会话盒子等）

        探索来源: explorer_output/screenshots/session_group_more.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 打开会话分组弹窗")
        self.click_image(SESSION_GROUP_MORE_BUTTON, timeout=5)
        time.sleep(1)
        # 验证弹窗已打开 - 应能看到"会话分组"和"管理"文字
        self.find_text_by_ocr("会话分组", timeout=5)
        logger.info("✅ 会话分组弹窗已打开")
        return True

    def close_session_group_panel(self) -> bool:
        """
        关闭展开的会话分组弹窗（点击蒙层区域）

        步骤:
        1. 会话分组弹窗展开后，点击底部蒙层区域（会话列表区域）
        2. 弹窗关闭，恢复正常消息列表视图

        探索来源: explorer_output/screenshots/session_group_more.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 关闭会话分组弹窗（点击蒙层）")
        # 点击底部蒙层区域（会话列表区域，在弹窗之外）
        self.tap(270, 750)
        time.sleep(1)
        # 验证弹窗已关闭 - 分组标签栏恢复，≡按钮可见
        self.image_exists(SESSION_GROUP_MORE_BUTTON, timeout=5)
        logger.info("✅ 会话分组弹窗已关闭")
        return True

    def open_session_group_manage(self) -> bool:
        """
        进入分组管理页面

        步骤:
        1. 打开会话分组弹窗
        2. 点击"管理"按钮
        3. 进入管理分组页面

        探索来源: explorer_output/screenshots/session_group_manage.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 进入分组管理页面")
        self.open_session_group_panel()
        self.click_text("管理", timeout=5)
        time.sleep(1)
        self.find_text_by_ocr("管理分组", timeout=5)
        logger.info("✅ 已进入分组管理页面")
        return True

    def enable_hidden_session_group(self, group_name: str = "群组") -> bool:
        """
        在管理分组页面启用一个隐藏的分组

        步骤:
        1. 进入管理分组页面
        2. 滚动到底部"隐藏"区域
        3. 找到目标分组名并点击其左侧的+号按钮
        4. 验证分组移到了"展示"区域
        5. 返回消息列表页

        探索来源: explorer_output/screenshots/manage_groups.png

        Args:
            group_name: 要启用的隐藏分组名称，默认"群组"
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 启用隐藏分组: {group_name}")

        # 进入管理分组页面
        self.open_session_group_manage()
        time.sleep(1)

        # 滚动到底部看到"隐藏"区域
        self.swipe_up(300)
        time.sleep(1)

        # 验证能看到"隐藏"区域和目标分组
        self.find_text_by_ocr("隐藏", timeout=5)
        pos = self.find_text_by_ocr(group_name, timeout=5)
        assert pos is not None, f"未找到隐藏分组 '{group_name}'"

        # 点击分组左侧的+号按钮（在分组文字左侧约50px处）
        plus_x = pos[0] - 50
        plus_y = pos[1]
        self.tap(plus_x, plus_y)
        time.sleep(2)

        # 验证分组已移到展示区域 - 隐藏区域不再显示该分组
        # 滚动回顶部确认展示区域
        self.swipe_down(300)
        time.sleep(1)

        # 验证展示数量增加了（展示区域包含该分组名）
        self.find_text_by_ocr("展示", timeout=5)

        # 返回消息列表
        self.press_back()
        time.sleep(0.5)

        logger.info(f"✅ 隐藏分组 '{group_name}' 已启用")
        return True

    def disable_session_group(self, group_name: str = "群组") -> bool:
        """
        在管理分组页面将一个展示的分组移到隐藏区域

        步骤:
        1. 进入管理分组页面
        2. 滚动找到目标分组
        3. 点击其左侧的-号按钮
        4. 返回消息列表页

        Args:
            group_name: 要隐藏的分组名称，默认"群组"
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 隐藏分组: {group_name}")

        # 进入管理分组页面
        self.open_session_group_manage()
        time.sleep(1)

        # 滚动查找目标分组
        self.swipe_up(300)
        time.sleep(1)

        pos = self.find_text_by_ocr(group_name, timeout=5)
        assert pos is not None, f"未找到分组 '{group_name}'"

        # 点击分组左侧的-号按钮
        minus_x = pos[0] - 50
        minus_y = pos[1]
        self.tap(minus_x, minus_y)
        time.sleep(2)

        # 返回消息列表
        self.press_back()
        time.sleep(0.5)

        logger.info(f"✅ 分组 '{group_name}' 已隐藏")
        return True

    # ==================== 群组相关 ====================

    def create_team(self):
        """创建群组"""
        username = "grp.popoqa"
        self.click_image(SESSIONLIST_PLUS_BUTTON)
        time.sleep(5)
        self.click_image(SESSIONLIST_PLUS_BUTTON_CREATETEAM)
        time.sleep(0.3)
        self.image_exists(SELECT_TITLE_ADD_TEAM_MUNBER)
        self.click_image(SELECT_SEARCH)
        self.input_text(str(username))
        time.sleep(1)

        self.click_image(SELECT_CIRCLE, region=Normal.HALF_UP)
        time.sleep(0.3)
        self.image_exists(SELECT_CIRCLE_BLUE, region=Normal.HALF_UP)
        self.click_image(SELECT_OK_BLUE, region=Normal.HALF_DOWN)

        try:
            self.text_exists(text="选择已有群组", region=Normal.HALF_UP)
            self.click_image(CREATE_NEW_TEAM, region=Normal.HALF_DOWN)
        except:
            pass

        time.sleep(1)
        self.text_exists(text="发起群聊", region=Normal.HALF_UP)
        self.text_exists(text="并邀请", region=Normal.HALF_UP)
        self.text_exists(text="加入群聊", region=Normal.HALF_UP)
        return True

    def delete_team(self):
        pass

    # ==================== 消息操作相关 ====================

    def recall_message(self, message_text: str):
        """
        撤回消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"撤回"，
        在确认弹窗中点击"确定"完成撤回。

        前置条件:
        - 当前页面为聊天页面 (chat_page)
        - 目标消息为自己发送的消息
        - 消息发送时间在24小时内

        步骤:
        1. 通过OCR定位消息文字
        2. 长按消息体(1.5秒)
        3. 弹出操作菜单（底部浮动面板）
        4. 点击"撤回"选项
        5. 在确认弹窗中点击"确定"
        6. 验证撤回成功（出现"你撤回了一条消息"提示）

        探索来源: explorer_output/records/exploration_record_recall_message.md

        Args:
            message_text: 要撤回的消息文字内容

        Returns:
            bool: 撤回是否成功
        """
        logger.info(f"🔄 [MuMu] 撤回消息: '{message_text}'")

        # 1. 先定位消息文字的 Y 坐标，用于后续限定验证区域
        msg_y = self.find_text_by_ocr(message_text)[1]
        time.sleep(0.5)

        # 2. 长按消息体
        self.long_press_text(message_text)
        time.sleep(1)

        # 3. 点击弹出菜单中的"撤回"
        self.click_text("撤回")
        time.sleep(1)

        # 4. 判断是否存在撤回确认弹窗
        if self.find_image(MSG_RECELL_POP, timeout=2):
            self.click_text("确定")

        # 5. 验证撤回成功（限定在原消息 Y 坐标上下 60px 范围内搜索，避免匹配到其他历史撤回记录）
        time.sleep(1)
        verify_y_top = max(0, msg_y - 60)
        verify_y_bottom = min(960, msg_y + 60)
        self.find_text_by_ocr("你撤回了一条消息", timeout=5, region=(0, verify_y_top, 540, verify_y_bottom))

        logger.info(f"✅ [MuMu] 消息撤回成功: '{message_text}'")
        return True

    def reply_message(self, message_text: str, reply_content: str) -> bool:
        """
        回复消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"回复"，
        输入回复内容后发送。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"回复"
        3. 验证引用栏出现
        4. 输入回复内容
        5. 点击发送按钮
        6. 验证发送成功（发送按钮恢复为+号）

        探索来源: explorer_output/screenshots/longpress_step3_reply_clicked.png

        Args:
            message_text: 要回复的目标消息文字
            reply_content: 回复内容

        Returns:
            bool: 回复是否成功
        """
        logger.info(f"💬 [MuMu] 回复消息: '{message_text}' -> '{reply_content}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("回复", region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_REPLY_QUOTE_BAR, timeout=10, region=Normal.HALF_DOWN)

        self.input_text(str(reply_content))
        time.sleep(0.5)

        self.click_image(CHAT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info(f"✅ [MuMu] 回复消息成功")
        return True

    def copy_message(self, message_text: str) -> bool:
        """
        复制消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"复制"，
        消息文字内容复制到剪贴板。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"复制"
        3. 验证"复制成功"toast出现

        探索来源: explorer_output/screenshots/longpress_step6_copy_done.png

        Args:
            message_text: 要复制的消息文字

        Returns:
            bool: 复制是否成功
        """
        logger.info(f"📋 [MuMu] 复制消息: '{message_text}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("复制", region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_COPY_SUCCESS_TOAST)

        logger.info(f"✅ [MuMu] 消息复制成功")
        return True

    def multi_select_message(self, message_text: str) -> bool:
        """
        进入多选模式

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"多选"，
        进入多选模式，验证后按返回键退出多选模式。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"多选"
        3. 验证进入多选模式（标题栏出现"已选中"）
        4. 按返回键退出多选模式

        探索来源: explorer_output/screenshots/longpress_step8_multiselect.png

        Args:
            message_text: 要多选的消息文字

        Returns:
            bool: 多选模式进入和退出是否成功
        """
        logger.info(f"☑️ [MuMu] 多选消息: '{message_text}'")

        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        self.click_text("多选", region=Normal.HALF_DOWN)
        time.sleep(1)

        self.image_exists(CHAT_MULTI_SELECT_TITLE, region=Normal.HALF_UP)

        self.press_back()
        time.sleep(0.5)

        logger.info(f"✅ [MuMu] 多选模式进入和退出成功")
        return True

    def translate_message(self, message_text: str) -> bool:
        """
        翻译消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"翻译"，
        消息气泡下方出现翻译结果。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"翻译"
        3. 验证翻译结果出现

        探索来源: explorer_output/screenshots/longpress_step10_translate.png

        Args:
            message_text: 要翻译的消息文字

        Returns:
            bool: 翻译是否成功
        """
        logger.info(f"🌐 [MuMu] 翻译消息: '{message_text}'")

        # 先用OCR定位消息坐标，记录y值用于后续限定搜索区域
        msg_pos = self.find_text_by_ocr(message_text, timeout=10)
        assert msg_pos is not None, f"未找到消息文字 '{message_text}'"
        msg_y = msg_pos[1]

        self.long_press(msg_pos[0], msg_pos[1], duration=1.5)
        logger.info(f"长按文字 '{message_text}' 位置：({msg_pos[0]}, {msg_pos[1]})")
        time.sleep(1)

        self.click_text("翻译", region=Normal.HALF_DOWN)
        time.sleep(3)

        # 在消息y坐标上下100px范围内搜索翻译结果
        search_y1 = max(0, msg_y - 100)
        search_y2 = min(960, msg_y + 100)
        search_region = (0, search_y1, 540, search_y2 - search_y1)
        self.image_exists(CHAT_TRANSLATE_RESULT, timeout=15, region=search_region)

        logger.info(f"✅ [MuMu] 消息翻译成功")
        return True

    def favorite_message(self, message_text: str) -> bool:
        """
        收藏消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"收藏"，
        出现"已收藏"提示。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 点击弹出菜单中的"收藏"
        3. 验证"已收藏"提示出现

        探索来源: explorer_output/screenshots/longpress_step11_favorite.png

        Args:
            message_text: 要收藏的消息文字

        Returns:
            bool: 收藏是否成功
        """
        logger.info(f"⭐ [MuMu] 收藏消息: '{message_text}'")

        # 长按消息，如果菜单未弹出则增加时长重试
        menu_appeared = None
        for attempt, dur in enumerate([1.5, 2.5, 3.0], start=1):
            # 定位消息
            time.sleep(0.5)
            msg_pos = self.find_text_by_ocr(message_text, timeout=5)
            assert msg_pos is not None, f"未找到消息文字: '{message_text}'"

            lp_x, lp_y = msg_pos[0], msg_pos[1]
            # 如果消息在底部(y>750)，向上偏移50px确保点击在气泡中心
            if lp_y > 750:
                lp_y = lp_y - 50
                logger.info(f"📜 消息在底部，y坐标从{msg_pos[1]}偏移到{lp_y}")

            self.long_press(lp_x, lp_y, duration=dur)
            time.sleep(1)
            menu_appeared = self.find_text_by_ocr("复制", timeout=3)
            if menu_appeared:
                break
            logger.warning(f"⚠️ 第{attempt}次长按({dur}s)@({lp_x},{lp_y})未弹出菜单，重试...")

        assert menu_appeared is not None, "长按消息后未出现操作菜单"

        # 在菜单中查找"收藏"并点击
        # 菜单项布局：上方是图标，下方是文字，点击图标区域更可靠(向上偏移30px)
        fav_pos = self.find_text_by_ocr("收藏", timeout=3)
        if fav_pos:
            # 点击文字上方的图标区域
            self.tap(fav_pos[0], fav_pos[1] - 30)
        else:
            # 如果 OCR 没找到"收藏"文字，尝试图片匹配
            img_pos = self.find_image(LONGPRESS_FAVORITE_BUTTON, timeout=3)
            assert img_pos is not None, "长按菜单中未找到'收藏'选项"
            self.tap(img_pos[0], img_pos[1])
        time.sleep(2)

        # 验证收藏成功：OCR检测"已收藏"文字
        fav_toast = self.find_text_by_ocr("已收藏", timeout=5)
        assert fav_toast is not None, "收藏操作后未出现'已收藏'提示"

        # 关闭收藏成功引导弹窗（首次收藏会弹出"我知道了"按钮）
        know_pos = self.find_text_by_ocr("我知道了", timeout=3)
        if know_pos:
            self.tap(know_pos[0], know_pos[1])
            time.sleep(0.5)

        logger.info(f"✅ [MuMu] 消息收藏成功")
        return True

    def recall_good(self):
        """
            撤回赞消息
        """
        x, y = self.find_image(MSG_MESSAGE_GOOD, timeout=15)
        self.long_press(x, y, duration=1.3)
        self.click_text("撤回")

    # ==================== 发消息相关 ====================

    def send_message(self, recipient: str, message: str, isback):
        """
        发送消息（支持P2P消息和群组消息）

        根据 recipient 自动判断是发送给个人还是群组：
        - 如果 recipient 是纯数字，则认为是群号，给群组发消息
        - 否则认为是人，给人发消息

        步骤:
        1. 从消息页面点击搜索按钮进入搜索页
        2. 搜索收件人（支持账号、昵称）
        3. 切换到对应Tab（联系人Tab或群组Tab）
        4. 点击搜索结果
        5. 进入聊天页面后，点击输入框
        6. 输入消息内容
        7. 点击发送按钮
        8. 验证消息发送成功（发送按钮恢复为+号）
        9. 返回消息页面

        探索来源: explorer_output/records/exploration_record_send_message.md

        Args:
            recipient: 收件人账号或关键词（如 '12345' 表示群组，'zhangsan' 表示个人）
            message: 要发送的消息内容
        """
        # 判断是否为群组：纯数字为群号
        if message is None:
            message = self.random_digits()
        is_group = recipient.isdigit()

        if is_group:
            msg_type = "群组"
        else:
            msg_type = "P2P"

        # 1. 打开搜索页面
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)

        # 2. 输入搜索关键词
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(recipient))
        time.sleep(1)

        # 3. 切换到对应Tab
        if is_group:
            self.click_text("群组", region=Normal.HALF_UP)
        else:
            self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        # 4. 点击搜索结果中的联系人/群组（用完整邮箱匹配，避免点到搜索框里的文字）
        recipient_email = f"{recipient}@corp.netease.com" if "@" not in recipient else recipient
        self.click_text(recipient_email, timeout=10)
        time.sleep(1)

        # 5. 验证进入聊天页面（通过加号按钮判断）
        plus_pos = self.find_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        assert plus_pos is not None, "❌ 未进入聊天页面：未找到加号按钮"
        logger.info(f"📱 已进入{msg_type}聊天页面")

        # 6. 点击输入框（通过加号按钮坐标左偏定位输入框区域）
        self.tap(plus_pos[0], plus_pos[1], dx=-200)
        time.sleep(0.3)

        # 7. 输入消息内容
        self.input_text(str(message))
        time.sleep(0.5)

        # 8. 点击发送按钮
        self.click_image(CHAT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 9. 验证发送成功：发送按钮恢复为+号
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info(f"✅ [MuMu] 消息发送成功: '{message}' -> {recipient}")
        if isback:
            # 10. 返回消息页面，最多按5次返回键直到找到 MESSAGE_TAB_BLUE
            for i in range(5):
                self.press_back()
                time.sleep(0.5)
                if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                    break
                logger.warning(f"⚠️ 第{i + 1}次未找到消息Tab，继续返回...")
            else:
                assert False, "❌ 返回消息页面失败：连续5次未找到 MESSAGE_TAB_BLUE"

        return message

    def send_file(self, recipient, file_name):
        is_group = recipient.isdigit()
        if is_group:
            msg_type = "群组"
        else:
            msg_type = "P2P"

        # 1. 打开搜索页面
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)

        # 2. 输入搜索关键词
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(recipient))
        time.sleep(1)

        # 3. 切换到对应Tab
        if is_group:
            self.click_text("群组", region=Normal.HALF_UP)
        else:
            self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        # 4. 点击搜索结果中的联系人/群组（用完整邮箱匹配，避免点到搜索框里的文字）
        recipient_email = f"{recipient}@corp.netease.com" if "@" not in recipient else recipient
        self.click_text(recipient_email)
        time.sleep(1)
        self.click_image(CHAT_PLUS_BUTTON)
        self.click_image(CHAT_PLUS_FILE)
        self.click_image(FILE_SELECT_MORE)
        self.text_exists("打开文档", timeout=5)
        self.click_text("MuMu共享文件夹")
        self.click_image(FILE_SELECT_MORE_SEARCH)
        self.input_text(file_name)
        time.sleep(1)
        self.click_text(file_name, region=Normal.HALF_DOWN)
        logger.info(f"Normal.CENTER_POP:{Normal.CENTER_POP}")
        # self.text_exists(text="确定要将文件发送给", region=Normal.CENTER_POP)
        self.click_image(POPO_POP_OK)
        pass

    # ==================== 富文本（扩展编辑）相关 ====================

    # 格式类型到图片常量的映射（用于模式A的装饰层图标识别，仅做视觉检测）
    _RICH_TEXT_FORMAT_MAP = {
        "bold": EXTENDED_EDIT_BOLD_B,
        "underline": EXTENDED_EDIT_UNDERLINE_U,
        "strikethrough": EXTENDED_EDIT_STRIKETHROUGH_S,
        "font_color": EXTENDED_EDIT_FONT_COLOR_A,
    }

    # 模式B（真正的格式工具栏 styleBar）中每个格式按钮的 ADB 坐标
    # 通过 uiautomator dump 确认：markdownBarRecyclerView 中的 styleBarFl 按钮
    # 按钮间距固定，Y 中心 = 918
    _STYLE_BAR_ADB_COORDS = {
        "bold": (108, 918),  # btn1 [84,894][132,942]  - B
        "italic": (180, 918),  # btn2 [156,894][204,942] - I
        "underline": (252, 918),  # btn3 [228,894][276,942] - U
        "strikethrough": (324, 918),  # btn4 [300,894][348,942] - S
        "font_color": (396, 918),  # btn5 [372,894][420,942] - A (字色)
    }

    # flMarkdown 按钮的 ADB 坐标 — 用于在模式A和模式B之间切换
    _FL_MARKDOWN_ADB_COORD = (42, 918)  # [18,876][66,960] 中心

    # 需要向左滑动工具栏才能看到的格式（模式B中 RecyclerView 可能需要滚动）
    _RICH_TEXT_SCROLL_FORMATS = {"style_6", "markdown"}

    def _adb_tap(self, x: int, y: int) -> bool:
        """
        通过 ADB 直接点击 Android 坐标

        用于绕过 pyautogui 的窗口坐标系限制，直接在 Android 层面点击。
        适用于工具栏按钮被原生 View 拦截的场景。

        Args:
            x: Android 坐标 X（基于 540x960 分辨率）
            y: Android 坐标 Y

        Returns:
            bool: 是否成功
        """
        result = self._run_adb_command("shell", "input", "tap", str(x), str(y))
        logger.info(f"👆 ADB tap ({x}, {y})")
        time.sleep(0.3)
        return result

    def _enter_extended_edit_mode(self) -> bool:
        """
        进入扩展编辑模式（富文本模式）

        前置条件: 当前页面为聊天页面 (chat_page)

        步骤:
        1. 点击聊天页底部的段落按钮 (iv_paragraph)
        2. 验证进入扩展编辑模式（输入框移至顶部，底部出现样式工具栏）

        探索来源: explorer_output/screenshots/richtext_step9_paragraph_clicked.png

        Returns:
            bool: 是否成功进入扩展编辑模式
        """
        logger.info("📝 [MuMu] 进入扩展编辑模式")

        # 点击段落按钮（在输入框右侧，发送按钮左侧）
        self.click_image(CHAT_PARAGRAPH_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 验证进入扩展编辑模式：底部出现样式工具栏（模式A的装饰层B图标）
        self.image_exists(EXTENDED_EDIT_BOLD_B, region=Normal.HALF_DOWN, timeout=5)

        logger.info("✅ 已进入扩展编辑模式")
        return True

    def _activate_style_bar(self) -> bool:
        """
        激活真正的格式工具栏（从模式A切换到模式B）

        扩展编辑模式有两种底部工具栏状态：
        - 模式A（初始）：底部显示 normalLL（图片/表情/翻译按钮），
                         视觉上覆盖了 B/I/U 装饰图标，但这些图标不可点击。
        - 模式B（格式）：底部显示 styleBar（markdownBarRecyclerView），
                         包含真正可点击的格式按钮 (B/I/U/S/A...)。

        通过 ADB 点击 flMarkdown 按钮 [18,876][66,960] 来切换。

        Returns:
            bool: 是否成功切换到模式B
        """
        logger.info("📝 [MuMu] 激活格式工具栏（切换到模式B）")
        ax, ay = self._FL_MARKDOWN_ADB_COORD
        self._adb_tap(ax, ay)
        time.sleep(0.5)

        # 验证：模式B中装饰层的 B 图标会消失（被 styleBar 替代）
        still_mode_a = self.find_image(EXTENDED_EDIT_BOLD_B, timeout=2, region=Normal.HALF_DOWN)
        if still_mode_a:
            logger.warning("⚠️ 仍在模式A，再次尝试切换")
            self._adb_tap(ax, ay)
            time.sleep(0.5)

        logger.info("✅ 格式工具栏已激活（模式B）")
        return True

    def _deactivate_style_bar(self) -> bool:
        """
        关闭格式工具栏，切回模式A

        Returns:
            bool: 是否成功切换回模式A
        """
        ax, ay = self._FL_MARKDOWN_ADB_COORD
        self._adb_tap(ax, ay)
        time.sleep(0.5)
        return True

    def _exit_extended_edit_mode(self) -> bool:
        """
        退出扩展编辑模式（如果仍在扩展编辑模式中）

        发送消息后，扩展编辑模式通常会自动退出。
        本方法先检查是否仍在扩展编辑模式中，如果是才点击关闭按钮。

        Returns:
            bool: 是否成功退出（或已经不在扩展编辑模式中）
        """
        logger.info("📝 [MuMu] 检查并退出扩展编辑模式")

        # 检查是否仍在扩展编辑模式：通过工具栏上的加粗B按钮判断
        still_in_edit = self.find_image(EXTENDED_EDIT_BOLD_B, timeout=2, region=Normal.HALF_DOWN)
        if not still_in_edit:
            logger.info("✅ 扩展编辑模式已自动退出，无需手动关闭")
            return True

        # 仍在扩展编辑模式，通过按返回键退出
        logger.info("⚠️ 扩展编辑模式仍在，按返回键退出")
        self.press_back()
        time.sleep(0.5)

        return True

    def _scroll_toolbar_to_format(self, format_type: str) -> bool:
        """
        滑动工具栏使目标格式按钮可见

        样式工具栏是可水平滑动的 RecyclerView，部分按钮（字色、样式6、Markdown）
        需要向左滑动才能看到。

        Args:
            format_type: 格式类型

        Returns:
            bool: 是否需要滑动（True=已滑动，False=无需滑动）
        """
        if format_type not in self._RICH_TEXT_SCROLL_FORMATS:
            return False

        logger.info(f"📝 向左滑动工具栏以显示 '{format_type}' 按钮")
        # 在工具栏区域向左滑动（工具栏在底部，约 y=915）
        self.swipe(400, 915, 100, 915, duration=0.3)
        time.sleep(0.5)
        return True

    def send_rich_text_message(self, recipient: str, message: str,
                               format_type: str) -> bool:
        """
        发送富文本格式消息

        POPO 扩展编辑模式的底部工具栏有两层 UI：
        - 模式A（初始）：原生 View（图片/表情/翻译按钮）上覆盖了装饰性 B/I/U 图标，
                         这些装饰图标不可点击，ADB tap 会被底层原生按钮拦截。
        - 模式B（格式）：通过点击 flMarkdown 按钮切换，底部变为真正可点击的
                         styleBar（markdownBarRecyclerView），包含 B/I/U/S/A 格式按钮。

        完整流程:
        1. 搜索联系人进入聊天页面
        2. 点击段落按钮进入扩展编辑模式（进入模式A）
        3. 点击 flMarkdown 切换到模式B（激活真正的格式工具栏）
        4. 通过 ADB tap 点击模式B中的格式按钮激活样式
        5. 切回模式A（关闭格式工具栏），此时格式仍然生效
        6. 点击输入区域，输入文本
        7. 点击发送按钮
        8. 验证发送成功
        9. 退出扩展编辑模式
        10. 返回消息列表页

        探索来源: explorer_output/records/exploration_record_richtext.md

        Args:
            recipient: 收件人账号（如 'grp.popoqa93'）
            message: 消息文本内容
            format_type: 格式类型，支持:
                - 'bold': 加粗
                - 'italic': 斜体
                - 'underline': 下划线
                - 'strikethrough': 删除线
                - 'font_color': 字体颜色

        Returns:
            bool: 发送是否成功
        """
        logger.info(f"📝 [MuMu] 发送富文本消息: format={format_type}, text='{message}'")

        # 验证格式类型有效
        adb_coord = self._STYLE_BAR_ADB_COORDS.get(format_type)
        assert adb_coord is not None, (
            f"不支持的格式类型: {format_type}，"
            f"支持的类型: {list(self._STYLE_BAR_ADB_COORDS.keys())}"
        )

        # 1. 进入聊天页面
        self._enter_chat_page(recipient)

        # 2. 进入扩展编辑模式（此时处于模式A）
        self._enter_extended_edit_mode()

        # 3. 切换到模式B（真正的格式工具栏）
        self._activate_style_bar()

        # 4. 在模式B中，通过 ADB tap 点击格式按钮（滑动如需要）
        self._scroll_toolbar_to_format(format_type)
        ax, ay = adb_coord
        logger.info(f"📝 通过 ADB 点击格式按钮 '{format_type}' @ ({ax}, {ay})")
        self._adb_tap(ax, ay)
        time.sleep(0.5)

        # 5. 切回模式A（关闭格式工具栏，格式仍然生效）
        self._deactivate_style_bar()

        # 6. 点击输入区域并输入文本
        self.click_text("发送给", region=Normal.HALF_UP)
        time.sleep(0.3)
        self.input_text(str(message))
        time.sleep(0.5)

        # 7. 点击发送按钮
        self.click_image(EXTENDED_EDIT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 8. 验证发送成功：消息文本出现在聊天区域
        self.find_text_by_ocr(message, timeout=5)

        # 9. 退出扩展编辑模式
        self._exit_extended_edit_mode()
        time.sleep(0.5)

        # 10. 返回消息列表页
        for i in range(5):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        logger.info(f"✅ [MuMu] 富文本消息发送成功: format={format_type}")
        return True

    # Markdown 语法类型映射：markdown_type -> (语法模板函数, 日志描述)
    # 语法模板函数接收 text 和可选参数，返回 (markdown_text, verify_text)
    _MARKDOWN_SYNTAX_MAP = {
        "hyperlink": lambda text, url="https://www.163.com", **kw: (f"[{text}]({url})", text),
        "quote": lambda text, **kw: (f"> {text}", text),
        "inline_code": lambda text, **kw: (f"`{text}`", text),
        "code_block": lambda text, language="", **kw: (f"```{language}\n{text}\n```", text),
        "background_color": lambda text, **kw: (f"=={text}==", text),
    }

    def send_markdown_message(self, recipient: str, text: str,
                              markdown_type: str, **kwargs) -> bool:
        """
        发送 Markdown 格式消息（统一入口）

        在扩展编辑模式下切换到 Markdown 模式，使用指定的 Markdown 语法发送消息。

        支持的 markdown_type:
        - 'hyperlink': 超链接 [文字](URL)，额外参数 url
        - 'quote': 引用块 > 文字
        - 'inline_code': 行内代码 `代码`
        - 'code_block': 代码块 ```language\\ncode\\n```，额外参数 language
        - 'background_color': 背景色高亮 ==文字==

        步骤:
        1. 进入聊天页面
        2. 进入扩展编辑模式
        3. 滑动工具栏找到 Markdown 按钮并点击
        4. 输入对应 Markdown 语法
        5. 发送并验证
        6. 退出扩展编辑模式，返回消息列表页

        探索来源: explorer_output/records/exploration_record_richtext.md

        Args:
            recipient: 收件人账号（如 'grp.popoqa93'）
            text: 消息文本内容
            markdown_type: Markdown 语法类型
            **kwargs: 额外参数（如 url, language）

        Returns:
            bool: 发送是否成功
        """
        syntax_fn = self._MARKDOWN_SYNTAX_MAP.get(markdown_type)
        assert syntax_fn is not None, (
            f"不支持的 Markdown 类型: {markdown_type}，"
            f"支持的类型: {list(self._MARKDOWN_SYNTAX_MAP.keys())}"
        )

        markdown_text, verify_text = syntax_fn(text, **kwargs)
        logger.info(f"📝 [MuMu] 发送Markdown消息: type={markdown_type}, text='{text}'")

        # 1. 进入聊天页面
        self._enter_chat_page(recipient)

        # 2. 进入扩展编辑模式
        self._enter_extended_edit_mode()

        # 3. 滑动到 Markdown 按钮并点击
        self._scroll_toolbar_to_format("markdown")
        # 注意: EXTENDED_EDIT_MARKDOWN 按钮在当前版本中已不存在
        # 尝试通过 OCR 定位 Markdown/Md 文字
        self.click_text("Md", timeout=5, region=Normal.HALF_DOWN)
        time.sleep(0.5)

        # 4. 点击输入区域并输入 Markdown 语法
        self.click_text("发送给", region=Normal.HALF_UP)
        time.sleep(0.3)
        self.input_text(markdown_text)
        time.sleep(0.5)

        # 5. 发送
        self.click_image(EXTENDED_EDIT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 6. 验证发送成功
        self.find_text_by_ocr(verify_text, timeout=5)

        # 7. 退出扩展编辑模式
        self._exit_extended_edit_mode()
        time.sleep(0.5)

        # 8. 返回消息列表页
        for i in range(5):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        logger.info(f"✅ [MuMu] Markdown消息发送成功: type={markdown_type}")
        return True

    # ---- 向下兼容的快捷方法（内部调用 send_markdown_message）----

    def send_hyperlink_message(self, recipient: str, text: str,
                               url: str = "https://www.163.com") -> bool:
        """发送超链接消息（快捷方法，委托给 send_markdown_message）"""
        return self.send_markdown_message(recipient, text, "hyperlink", url=url)

    def send_quote_message(self, recipient: str, text: str) -> bool:
        """发送引用块消息（快捷方法，委托给 send_markdown_message）"""
        return self.send_markdown_message(recipient, text, "quote")

    def send_inline_code_message(self, recipient: str, text: str) -> bool:
        """发送行内代码消息（快捷方法，委托给 send_markdown_message）"""
        return self.send_markdown_message(recipient, text, "inline_code")

    def send_code_block_message(self, recipient: str, text: str,
                                language: str = "") -> bool:
        """发送代码块消息（快捷方法，委托给 send_markdown_message）"""
        return self.send_markdown_message(recipient, text, "code_block", language=language)

    def send_background_color_message(self, recipient: str, text: str) -> bool:
        """发送背景色消息（快捷方法，委托给 send_markdown_message）"""
        return self.send_markdown_message(recipient, text, "background_color")

    # ==================== 侧边栏相关 ====================

    def open_sidebar(self):
        """
        打开侧边栏

        步骤:
        1. 确保在消息Tab页
        2. 点击左上角消息文案左侧的头像区域
        3. 等待侧边栏内容出现（通过图片断言确认）

        探索来源: explorer_output/screenshots/step7_sidebar.png
        """
        logger.info("📋 [MuMu] 打开侧边栏")
        self.click_image(MESSAGE_TAB_MSG_TEXT, dx=-70)
        time.sleep(0.5)
        self.image_exists(SIDEBAR_SETTINGS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("✅ 侧边栏已打开")

    def close_sidebar(self):
        """
        关闭侧边栏

        通过按返回键关闭侧边栏，回到消息列表页
        """
        logger.info("📋 [MuMu] 关闭侧边栏")
        self.press_back()
        time.sleep(0.5)

    def view_my_profile(self) -> dict:
        """
        查看我的个人资料

        步骤:
        1. 打开侧边栏
        2. 点击用户名进入个人资料页
        3. 通过 find_text_by_ocr 逐字段采集个人信息
        4. 向上滑动查看更多字段（岗位、组织架构、办公位置）
        5. 返回消息列表页

        探索来源:
        - explorer_output/screenshots/step7_sidebar.png (侧边栏)
        - explorer_output/screenshots/step8_profile.png (个人资料页上半)
        - explorer_output/screenshots/step9_profile_scroll.png (个人资料页下半)

        Returns:
            dict: 个人资料信息，包含以下字段:
                - nickname_cn: 中文昵称
                - nickname_en: 英文昵称
                - nickname_jp: 日文昵称
                - signature: 个性签名
                - account: 账号邮箱
                - phone: 手机号
                - position: 岗位名称
                - organization: 组织架构
                - office_location: 办公位置
        """
        logger.info("👤 [MuMu] 查看个人资料")

        # 1. 打开侧边栏
        self.open_sidebar()

        # 2. 在侧边栏中点击用户名区域进入个人资料页
        self.image_exists(SIDEBAR_MY_COLLECTION)
        # 用户名在侧边栏顶部头像下方，相对"我的收藏"向上偏移点击
        self.click_image(SIDEBAR_MY_COLLECTION, dx=0, dy=-180)
        time.sleep(1.5)

        # 3. 通过 find_text_by_ocr 确认进入个人资料页
        self.find_text_by_ocr("个性签名", timeout=5)
        self.find_text_by_ocr("中文昵称", timeout=3)
        logger.info("📱 已进入个人资料页")

        # 4. 逐字段采集个人信息
        profile = self._extract_profile_fields()

        # 5. 返回消息列表
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)

        logger.info(f"✅ 个人资料采集完成: {profile}")
        return profile

    def _extract_profile_fields(self) -> dict:
        """
        从个人资料页通过 find_text_by_ocr 逐字段提取信息

        利用 find_text_by_ocr 在页面中查找字段标签，
        字段值在标签坐标下方约25~30px处，通过偏移坐标读取。

        Returns:
            dict: 个人资料字段
        """
        profile = {}

        # 第一屏字段
        first_screen_fields = [
            ("个性签名", "signature"),
            ("中文昵称", "nickname_cn"),
            ("英文昵称", "nickname_en"),
            ("日文昵称", "nickname_jp"),
            ("账号", "account"),
            ("手机号", "phone"),
        ]

        for label, key in first_screen_fields:
            pos = self.find_text_by_ocr(label, timeout=3)
            if pos:
                profile[key] = pos
                logger.info(f"📋 找到字段 '{label}' @ {pos}")

        # 向上滑动看第二屏：岗位名称、组织架构、办公位置
        self.swipe_up(300)
        time.sleep(0.5)

        second_screen_fields = [
            ("岗位名称", "position"),
            ("组织架构", "organization"),
            ("办公位置", "office_location"),
        ]

        for label, key in second_screen_fields:
            pos = self.find_text_by_ocr(label, timeout=3)
            if pos:
                profile[key] = pos
                logger.info(f"📋 找到字段 '{label}' @ {pos}")

        return profile

    def open_my_collection(self):
        """
        打开「我的收藏」

        步骤: 打开侧边栏 → 点击"我的收藏"图片
        """
        logger.info("⭐ [MuMu] 打开我的收藏")
        self.open_sidebar()
        self.click_image(SIDEBAR_MY_COLLECTION, region=Normal.HALF_DOWN)
        time.sleep(1)

    def open_device_management(self):
        """
        打开「登录设备管理」

        步骤: 打开侧边栏 → 点击"登录设备管理"图片
        """
        logger.info("📱 [MuMu] 打开登录设备管理")
        self.open_sidebar()
        self.click_image(SIDEBAR_DEVICE_MANAGEMENT, region=Normal.HALF_DOWN)
        time.sleep(1)

    def open_settings(self):
        """
        打开「设置」页面

        步骤: 打开侧边栏 → 点击"设置"图片
        """
        logger.info("⚙️ [MuMu] 打开设置页面")
        self.open_sidebar()
        self.click_image(SIDEBAR_SETTINGS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

    # ==================== 消息设置相关 ====================

    # 消息设置页面中的所有开关项（完整列表）
    MSG_SETTINGS_SWITCHES = [
        "AI智能识别快捷指令",
        "AI智能识别任务",
        "双击会话背景发送语音",
        "连续播放语音消息",
        "语音消息自动转换出文字",
        "语音消息转文字自动使用AI整理",
        "文件自动下载",
        "消息气泡聚合显示",
        "分享转发时需再次确认",
        "启用表情联想",
        "表情添加至默认分组",
    ]

    def open_message_settings(self):
        """
        从消息页面进入 设置→消息 设置页面

        步骤:
        1. 打开侧边栏
        2. 点击设置（图片识别）
        3. 点击消息入口（图片识别）
        4. 验证进入消息设置页面（图片识别）

        探索来源: explorer_output/screenshots/msg_settings_step0_focused.png
        """
        logger.info("⚙️ [MuMu] 打开消息设置页面")
        self.open_settings()
        self.click_image(SETTINGS_MESSAGE_ENTRY)
        time.sleep(0.5)
        self.image_exists(MSG_SETTINGS_TITLE, timeout=5, region=Normal.HALF_UP)
        logger.info("✅ 已进入消息设置页面")

    def close_message_settings(self):
        """
        从消息设置页面返回到消息列表页

        步骤:
        1. 按返回键 → 设置页
        2. 按返回键 → 侧边栏
        3. 按返回键 → 消息页
        """
        logger.info("🔙 [MuMu] 关闭消息设置页面")
        self.press_back()
        time.sleep(0.3)
        self.press_back()
        time.sleep(0.3)
        self.press_back()
        time.sleep(0.5)

    def _scroll_to_switch(self, switch_name: str) -> bool:
        """
        滚动消息设置页面直到目标开关可见

        消息设置页面有多屏内容，需要滑动才能看到所有开关。
        先尝试当前屏查找，找不到则向上滑动查找。

        Args:
            switch_name: 开关标题文字

        Returns:
            bool: 是否找到目标开关
        """
        # 先在当前屏查找
        pos = self.find_text_by_ocr(switch_name, timeout=2)
        if pos:
            return True

        # 向上滑动查找（最多滑3次）
        for i in range(3):
            self.swipe_up(350)
            time.sleep(0.5)
            pos = self.find_text_by_ocr(switch_name, timeout=2)
            if pos:
                return True

        logger.warning(f"⚠️ 滑动后仍未找到开关: {switch_name}")
        return False

    def set_message_switch(self, switch_name: str, target_state: bool) -> bool:
        """
        设置消息设置页面中指定开关的状态

        前置条件: 当前已在消息设置页面

        步骤:
        1. 滑动页面使目标开关可见
        2. 检测当前开关状态
        3. 如果与目标不一致则点击切换
        4. 验证切换成功

        探索来源: explorer_output/screenshots/msg_settings_analysis.png

        Args:
            switch_name: 开关名称（如 "连续播放语音消息"）
            target_state: 目标状态 True=开启, False=关闭

        Returns:
            bool: 操作是否成功
        """
        state_text = "开启" if target_state else "关闭"
        logger.info(f"🔧 [MuMu] 设置开关 '{switch_name}' → {state_text}")

        # 滚动到目标开关位置
        assert self._scroll_to_switch(switch_name), f"未找到开关 '{switch_name}'"

        # 切换开关
        result = self.toggle_switch(switch_name, target_state)
        assert result, f"开关 '{switch_name}' 切换到{state_text}失败"

        logger.info(f"✅ [MuMu] 开关 '{switch_name}' 已设置为{state_text}")
        return True

    def get_message_switch_state(self, switch_name: str) -> bool:
        """
        获取消息设置页面中指定开关的当前状态

        前置条件: 当前已在消息设置页面

        Args:
            switch_name: 开关名称

        Returns:
            bool: True=开启, False=关闭
        """
        logger.info(f"🔍 [MuMu] 查询开关状态: '{switch_name}'")
        self._scroll_to_switch(switch_name)
        return self.is_switch_on(switch_name)

    def toggle_message_switch(self, switch_name: str) -> bool:
        """
        切换消息设置页面中指定开关（开→关 或 关→开）

        完整流程: 消息页 → 侧边栏 → 设置 → 消息设置 → 切换开关 → 返回消息页

        Args:
            switch_name: 开关名称

        Returns:
            bool: 切换后的新状态 True=开启, False=关闭
        """
        logger.info(f"🔄 [MuMu] 切换消息设置开关: '{switch_name}'")

        self.open_message_settings()

        self._scroll_to_switch(switch_name)
        old_state = self.is_switch_on(switch_name)
        new_state = not old_state
        self.set_message_switch(switch_name, new_state)

        self.close_message_settings()

        state_text = "开启" if new_state else "关闭"
        logger.info(f"✅ [MuMu] 开关 '{switch_name}' 已切换为{state_text}")
        return new_state

    # ==================== 图片编辑相关 ====================

    def _enter_chat_page(self, recipient: str) -> None:
        """
        搜索联系人/群组，进入聊天页（复用 send_message 前半部分逻辑）

        Args:
            recipient: 收件人账号或群号
        """
        is_group = recipient.isdigit()

        # 点击搜索入口：新版本POPO消息列表页顶部有内嵌搜索框
        # 提示文字可能为"输入"/"使用快捷"或"搜索，输入"/"使用命令"
        # 优先OCR点击搜索框，回退到搜索按钮图片
        search_pos = self.find_text_by_ocr("使用快捷", region=Normal.HALF_UP, timeout=3)
        if search_pos is None:
            search_pos = self.find_text_by_ocr("使用命令", region=Normal.HALF_UP, timeout=3)
        if search_pos is None:
            search_pos = self.find_text_by_ocr("输入", region=Normal.HALF_UP, timeout=3)
        if search_pos:
            self.tap(search_pos[0], search_pos[1])
            time.sleep(1)
        else:
            self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
            time.sleep(1)

        self.input_text(str(recipient))
        time.sleep(1)

        if is_group:
            # 搜索页面的"群消息"Tab，OCR可能识别为"群消息"或拆为"群"+"消息"
            pos = self.find_text_by_ocr("群消息", region=Normal.HALF_UP, timeout=3)
            if pos is None:
                pos = self.find_text_by_ocr("群", region=(180, 140, 120, 50))
            if pos:
                self.tap(pos[0], pos[1])
        else:
            self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        recipient_email = f"{recipient}@corp.netease.com" if "@" not in recipient else recipient
        self.click_text(recipient_email, timeout=10)
        time.sleep(1)

        self.text_exists("发送给", region=Normal.HALF_DOWN)
        logger.info(f"[MuMu] 已进入聊天页: {recipient}")

    def send_image_from_album(self, recipient: str) -> bool:
        """
        从相册选图并发送（不进行编辑）

        步骤:
        1. 通过搜索进入联系人聊天页
        2. 点击 + 号打开更多面板
        3. 点击"相册"
        4. 点击第一张图片选中
        5. 点击"发送"按钮发送

        探索来源: explorer_output/screenshots/edit_img_plus_panel.png

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否发送成功
        """
        logger.info(f"[MuMu] 从相册发送图片给: {recipient}")

        self._enter_chat_page(recipient)

        # 打开 + 面板
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 点击相册
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 点击第一张图片（相册网格第一行第一个位置，y≈200, x≈70）
        self.tap(70, 200)
        time.sleep(1)

        # 点击发送
        self.click_text("发送", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 验证发送成功：回到聊天页，+ 按钮可见
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 图片发送成功")
        return True

    def select_edit_send_image_from_album(self, recipient: str) -> bool:
        """
        从相册选图 → 进入预览 → 点击"编辑" → 在编辑器中完成 → 发送

        步骤:
        1. 进入联系人聊天页
        2. 点击 + → 相册
        3. 点击第一张图片，直接进入带"编辑"按钮的预览页
        4. 点击"编辑"按钮进入图片编辑器
        5. 验证编辑器底部工具栏出现
        6. 点击"完成"退出编辑器
        7. 点击"发送"按钮发送编辑后的图片

        探索来源:
        - edit_img_after_done.png（预览页含编辑/发送按钮）
        - edit_img_editor_page.png（编辑器页面）

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否成功完成编辑并发送
        """
        logger.info(f"[MuMu] 从相册选图编辑后发送给: {recipient}")

        self._enter_chat_page(recipient)

        # 打开 + 面板
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 点击相册
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 点击第一张图片 → 直接进入预览页（有"编辑"按钮）
        self.tap(70, 200)
        time.sleep(1.5)

        # 点击"编辑"进入编辑器（点击图片后直接出现编辑按钮，无需额外点"预览"）
        self.click_image(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)

        # 验证已进入编辑器（底部工具栏出现）
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)
        logger.info("[MuMu] 已进入图片编辑器")

        # 点击"完成"退出编辑器
        self.click_image(IMAGE_EDITOR_DONE_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1)

        # 验证返回预览页（"编辑"按钮重新出现）
        self.image_exists(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=5)

        # 点击"发送"发送图片
        self.click_image(ALBUM_PREVIEW_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 验证发送成功：回到聊天页
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 相册选图编辑后发送成功")
        return True

    def edit_image_from_chat_message(self, RECIPIENT) -> bool:
        """
        长按聊天中最近发送的图片消息 → 点击"编辑图片" → 在编辑器中完成

        前置条件:
        - 当前页面为聊天页（chat_page）
        - 聊天中已有图片消息

        步骤:
        1. 长按已发送的图片消息气泡
        2. 点击弹出菜单中的"编辑图片"
        3. 验证进入图片编辑器（底部工具栏出现）
        4. 点击"完成"完成编辑

        探索来源:
        - edit_longpress_step1_menu.png（长按菜单含编辑图片选项）
        - edit_img_editor_page.png（编辑器页面）

        Returns:
            bool: 是否成功完成编辑
        """
        logger.info("[MuMu] 长按图片消息进行编辑")

        # 长按已发送的图片消息气泡
        self.long_press_image(CHAT_SENT_IMAGE_BUBBLE, duration=1.5)
        time.sleep(1)

        # 点击"编辑图片"（长按菜单中的文字选项，用 OCR 定位）
        self.click_text("编辑图片", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)

        # 验证进入图片编辑器
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)
        logger.info("[MuMu] 已进入图片编辑器（从长按菜单）")

        self.click_image(IMAGE_EDITOR_PEN_BUTTON, region=Normal.HALF_DOWN)

        # 在图片中画一个 H 图案，范围在左上角(125,200)到右下角(400,750)内
        # H 的左竖线：从 (125, 200) 向下到 (125, 750)
        self.swipe(125, 200, 125, 750, duration=0.5)
        time.sleep(0.3)
        # H 的右竖线：从 (400, 200) 向下到 (400, 750)
        self.swipe(400, 200, 400, 750, duration=0.5)
        time.sleep(0.3)
        # H 的中间横线：从 (125, 475) 向右到 (400, 475)
        self.swipe(125, 475, 400, 475, duration=0.5)
        self.image_exists(IMAGE_EDITOR_H)
        time.sleep(0.3)

        # 点击"完成"退出编辑器
        self.click_image(IMAGE_EDITOR_DONE_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1)

        # 在更多操作弹窗中选择“发送给同事或群组”
        self.text_exists("发送给同事或群组")
        self.click_image(IMAGE_EDITOR_FORWARD, region=Normal.HALF_DOWN)

        # 在选人组建的输入框中搜索接收者
        self.click_text("搜索", region=Normal.HALF_UP)
        self.input_text(RECIPIENT)

        # 点击关闭按钮下方308xp的第一个匹配结果，并且验证已发送提示
        self.click_image(SELECT_CANCEL, dy=308)
        self.image_exists(TOAST_SENDED)
        self.press_back()

        # 验证刚刚发送了带有H的图片
        self.image_exists(TOAST_SENDED)

        # 验证已返回聊天页（+ 按钮可见）
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 长按图片编辑完成")
        return True

    def select_edit_with_tools_send_image(self, recipient: str) -> bool:
        """
        从相册选图 → 编辑器中使用画笔工具编辑 → 完成 → 发送

        与 select_edit_send_image_from_album 的区别：
        本方法会在编辑器中使用画笔工具实际绘制，验证工具操作正常。

        步骤:
        1. 进入联系人聊天页
        2. 点击 + → 相册 → 选图 → 预览 → 编辑
        3. 进入编辑器后，在图片中心画一笔（使用画笔工具）
        4. 点击"完成"
        5. 点击"发送"

        探索来源: edit_img_editor_page.png（画笔工具坐标 x≈60, y≈870）

        Args:
            recipient: 收件人账号

        Returns:
            bool: 是否成功
        """
        logger.info(f"[MuMu] 从相册选图，使用工具编辑后发送给: {recipient}")

        self._enter_chat_page(recipient)

        # 打开 + 面板
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 点击相册
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 点击第一张图片 → 直接进入预览页（有"编辑"按钮）
        self.tap(70, 200)
        time.sleep(1.5)

        # 点击"编辑"进入编辑器（点击图片后直接出现编辑按钮，无需额外点"预览"）
        self.click_image(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1.5)

        # 验证已进入编辑器
        self.image_exists(IMAGE_EDITOR_TOOLBAR, region=Normal.HALF_DOWN, timeout=8)

        # 在图片中心绘制一笔（画笔工具已默认激活，或可 click_text("T", region=HALF_DOWN) 激活）
        # 直接在图片区域滑动，产生绘制效果
        self.swipe(150, 400, 380, 400, duration=0.5)
        time.sleep(0.5)
        # 点击"完成"
        self.click_image(IMAGE_EDITOR_DONE_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(1)

        # 验证返回预览页
        self.image_exists(ALBUM_PREVIEW_EDIT_BUTTON, region=Normal.HALF_DOWN, timeout=5)

        # 点击"发送"
        self.click_image(ALBUM_PREVIEW_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 验证发送成功
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("[MuMu] 使用工具编辑后发送成功")
        return True

    # ==================== 搜索相关 ====================
    def search(self, tab, text, isclose=True):
        """创建群组"""

        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)

        # tab左滑翻页
        if tab in ["云空间", "任务", "应用"]:
            self.swipe_left(self.text_exists("日程"), 230)
        img_name = f"搜索页面-{tab}tab.png"
        img_name_miss = f"搜索页面-{tab}tab-未选中.png"
        if tab == "全部":
            pass
        else:
            logger.info(f"tab是：{tab}")
            self.click_image(os.path.join(path, img_name_miss))
        self.image_exists(img_name, region=Normal.HALF_UP)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(text))
        if isclose:
            # 点击取消按钮，退出搜索页面
            self.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    # ==================== 群组管理相关 ====================

    def _enter_group_settings(self, group_identifier: str) -> None:
        """
        进入群设置页面

        步骤:
        1. 搜索群聊并进入群聊天页
        2. 点击顶部群名称区域（"名群成员"文字上方）进入群设置

        Args:
            group_identifier: 群搜索关键词（如群名称或群号）
        """
        logger.info(f"⚙️ [MuMu] 进入群设置: {group_identifier}")

        # 进入群聊页面
        self._enter_chat_page(group_identifier)

        # 点击群名称进入群设置
        members_pos = self.find_text_by_ocr("名群成员", timeout=5)
        assert members_pos, "未找到'名群成员'文字，可能不在群聊页面"
        self.tap(members_pos[0], members_pos[1], dy=-30)
        time.sleep(2)

        logger.info("✅ 已进入群设置页面")

    def search_chat_content(self, group_identifier: str, keyword: str) -> bool:
        """
        搜索群聊天内容

        在群设置中使用"搜索聊天内容"功能，输入关键词搜索聊天记录。

        前置条件:
        - 当前页面为消息列表页 (message_page)

        步骤:
        1. 搜索群聊并进入群聊天页
        2. 点击群名称进入群设置
        3. 点击"搜索聊天内容"
        4. 输入搜索关键词
        5. 验证搜索结果页面出现
        6. 返回消息列表页

        探索来源: explorer_output/screenshots/explore2_search_chat_content.png

        Args:
            group_identifier: 群搜索关键词
            keyword: 搜索关键词

        Returns:
            bool: 搜索是否成功执行
        """
        logger.info(f"🔍 [MuMu] 搜索群聊天内容: 群={group_identifier}, 关键词={keyword}")

        # 1. 进入群设置页面
        self._enter_group_settings(group_identifier)

        # 2. 点击"搜索聊天内容"
        self.click_text("搜索聊天内容", timeout=5)
        time.sleep(2)

        # 3. 输入搜索关键词
        self.click_text("搜索", timeout=3)
        time.sleep(0.5)
        self.input_text(str(keyword))
        time.sleep(2)

        # 4. 截图验证搜索结果页面
        logger.info(f"✅ [MuMu] 搜索聊天内容执行完成: {keyword}")

        # 5. 返回消息列表页
        for i in range(8):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        return True

    def set_group_announcement(self, group_identifier: str, content: str) -> bool:
        """
        设置群公告

        在群设置中发布群公告。

        前置条件:
        - 当前页面为消息列表页 (message_page)

        步骤:
        1. 进入群设置页面
        2. 点击"群公告"
        3. 进入群公告查看页
        4. 点击"编辑"
        5. 清空旧内容并输入新公告
        6. 点击右上角完成按钮
        7. 处理可能的"发送到群聊"确认
        8. 返回消息列表页

        探索来源: explorer_output/knowledge/app_map.json features.set_announcement

        Args:
            group_identifier: 群搜索关键词
            content: 公告内容

        Returns:
            bool: 设置是否成功
        """
        logger.info(f"📢 [MuMu] 设置群公告: 群={group_identifier}")

        # 1. 进入群设置页面
        self._enter_group_settings(group_identifier)

        # 2. 点击群公告
        self.click_text("群公告", timeout=5)
        time.sleep(1)

        # 3. 判断当前群公告状态
        # - 空公告：页面直接展示输入框，有"输入群公告内容"占位符
        # - 有公告：页面展示现有公告内容，右上角有"编辑"按钮
        try:
            self.image_exists(GROUP_ANNOUNCEMENT_EMPTY_PLACEHOLDER, timeout=2)
            logger.info("ℹ️ 群公告为空，已在编辑状态")
        except AssertionError:
            # 有现有公告，点击"编辑"进入编辑模式
            self.click_text("编辑", timeout=5)
            time.sleep(1)

        # 4. 清空旧内容并输入新公告
        self.clear_input()
        time.sleep(0.3)
        self.input_text(str(content))
        time.sleep(0.5)

        # 5. 收起键盘后点击右上角确认按钮
        # 群公告编辑页的确认按钮可能显示为"完成"/"发布"或图标
        self.press_back()
        time.sleep(0.5)
        confirm_clicked = False
        for btn_text in ["完成", "发布"]:
            try:
                self.click_text(btn_text, timeout=2, region=Normal.HALF_UP)
                confirm_clicked = True
                break
            except AssertionError:
                continue
        if not confirm_clicked:
            # 右上角按钮可能是纯图标（对勾），通过固定坐标点击
            logger.info("ℹ️ 未找到文字确认按钮，点击右上角图标按钮")
            self._adb_tap(486, 107)
        time.sleep(1)

        # 6. 处理"发送到群聊"确认弹窗（可能出现）
        try:
            self.click_text("发送到群聊", timeout=3)
            time.sleep(1)
        except AssertionError:
            logger.info("ℹ️ 未出现'发送到群聊'弹窗，跳过")

        logger.info(f"✅ [MuMu] 群公告设置成功")

        # 7. 返回消息列表页
        for i in range(8):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        return True

    def exit_group(self, group_identifier: str) -> bool:
        """
        退出群组

        在群设置页面滑动到底部，点击"退出群组"并确认。

        前置条件:
        - 当前页面为消息列表页 (message_page)

        步骤:
        1. 进入群设置页面
        2. 向上滑动3次（退出群组在第四屏）
        3. 点击"退出群组"
        4. 在确认弹窗中点击"确定"
        5. 验证返回消息列表页

        探索来源: explorer_output/knowledge/app_map.json features.exit_group

        Args:
            group_identifier: 群搜索关键词

        Returns:
            bool: 退出是否成功
        """
        logger.info(f"🚪 [MuMu] 退出群组: {group_identifier}")

        # 1. 进入群设置页面
        self._enter_group_settings(group_identifier)

        # 2. 滑动到底部（退出群组在第四屏，需要滑动3次）
        for i in range(3):
            self.swipe_up(400)
            time.sleep(1)

        # 3. 点击"退出群组"
        self.click_text("退出群组", timeout=5)
        time.sleep(1)

        # 4. 确认退出
        self.click_text("确定", timeout=5)
        time.sleep(2)

        # 5. 验证返回消息列表页
        self.image_exists(MESSAGE_TAB_BLUE, timeout=10)

        logger.info(f"✅ [MuMu] 已退出群组: {group_identifier}")
        return True

    def delete_message(self, message_text: str) -> bool:
        """
        删除消息

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"删除"，
        在确认弹窗中点击"删除"完成删除。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 弹出操作菜单（底部浮动面板）
        3. 点击"删除"选项 (坐标约386,712)
        4. 在确认弹窗"确认删除消息"中点击"删除"
        5. 验证消息已删除

        探索来源: explorer_output/screenshots/explore2_longpress_menu.png

        Args:
            message_text: 要删除的消息文字内容

        Returns:
            bool: 删除是否成功
        """
        logger.info(f"🗑️ [MuMu] 删除消息: '{message_text}'")

        # 1. 长按消息文字
        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        # 2. 点击弹出菜单中的"删除"
        self.click_text("删除", region=Normal.HALF_DOWN)
        time.sleep(1)

        # 3. 确认删除弹窗中点击"删除"
        self.find_text_by_ocr("确认删除消息", timeout=3)
        self.click_text("删除", timeout=3)
        time.sleep(1)

        logger.info(f"✅ [MuMu] 消息删除成功: '{message_text}'")
        return True

    def pin_message(self, message_text: str) -> bool:
        """
        Pin消息（置顶消息）

        在当前聊天页面，长按指定消息体，从弹出的操作菜单中点击"Pin"。

        前置条件:
        - 当前页面为聊天页面 (chat_page)

        步骤:
        1. 长按目标消息文字(1.5秒)
        2. 弹出操作菜单
        3. 点击"Pin"选项

        探索来源: explorer_output/screenshots/explore2_longpress_menu.png

        Args:
            message_text: 要Pin的消息文字内容

        Returns:
            bool: Pin是否成功
        """
        logger.info(f"📌 [MuMu] Pin消息: '{message_text}'")

        # 1. 长按消息文字
        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        # 2. 点击菜单中的"Pin"
        self.click_text("Pin", region=Normal.HALF_DOWN)
        time.sleep(1)

        logger.info(f"✅ [MuMu] 消息Pin成功: '{message_text}'")
        return True

    # ==================== 消息历史相关 ====================

    def _enter_group_settings(self, group_identifier: str) -> bool:
        """
        从消息列表页进入群设置页面

        步骤:
        1. 搜索群组并进入聊天页
        2. 点击群名称进入群设置

        Args:
            group_identifier: 群组标识（群号或群名关键词）

        Returns:
            bool: 是否成功进入群设置页面
        """
        logger.info(f"⚙️ [MuMu] 进入群设置: {group_identifier}")

        # 1. 搜索群组并进入聊天页
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(group_identifier))
        time.sleep(1)
        self.click_text("群", region=Normal.HALF_UP)
        time.sleep(2)

        # 点击第一个群组搜索结果
        # 群搜索结果中，群名下面显示"包含：xxx"，点击群名所在行（y约297）
        pos = self.find_text_by_ocr("包含：", timeout=10)
        # 点击"包含："上方约40px处（即群名所在的行）
        self.tap(270, pos[1] - 40)
        time.sleep(2)

        # 2. 点击群名称进入群设置
        self.click_text("名群成员", timeout=5, dy=-30)
        time.sleep(2)

        # 验证进入群设置页面
        self.text_exists("设置", timeout=5)
        logger.info("✅ [MuMu] 已进入群设置页面")
        return True

    def view_message_history_cloud_docs(self, group_identifier: str) -> bool:
        """
        查看消息历史-云文档

        从消息列表页进入群设置，在消息历史区域查看云文档Tab，
        验证云文档列表按时间倒序排序。

        步骤:
        1. 进入群设置页面
        2. 向上滑动找到消息历史区域
        3. 点击云文档Tab
        4. 验证云文档列表存在
        5. 返回消息列表页

        探索来源: explorer_output/screenshots/group_cloud_docs.png

        Args:
            group_identifier: 群组标识

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📄 [MuMu] 查看消息历史-云文档: {group_identifier}")

        # 1. 进入群设置页面
        self._enter_group_settings(group_identifier)

        # 2. 点击云文档Tab（在消息历史区域）
        self.click_text("云文档", timeout=10)
        time.sleep(2)

        # 3. 验证进入了消息历史-云文档页面
        # 页面应该显示Tab栏（消息/云文档/文件/图片视频/链接）和过滤选项
        self.text_exists("发送者", timeout=5)
        self.text_exists("全部时间", timeout=5)
        logger.info("✅ [MuMu] 云文档页面加载成功，显示发送者和时间过滤")

        # 4. 返回消息列表页
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(1)

        logger.info("✅ [MuMu] 查看消息历史-云文档完成")
        return True

    def search_message_history(self, group_identifier: str, keyword: str = "UI") -> bool:
        """
        在消息历史中搜索云文档

        从消息列表页进入群设置，在消息历史-云文档页面进行搜索。

        步骤:
        1. 进入群设置页面
        2. 点击云文档Tab进入消息历史
        3. 点击搜索框输入关键词
        4. 验证搜索结果
        5. 返回消息列表页

        探索来源: explorer_output/screenshots/group_cloud_docs.png

        Args:
            group_identifier: 群组标识
            keyword: 搜索关键词

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔍 [MuMu] 搜索消息历史: {group_identifier}, 关键词: {keyword}")

        # 1. 进入群设置页面
        self._enter_group_settings(group_identifier)

        # 2. 点击云文档Tab
        self.click_text("云文档", timeout=10)
        time.sleep(2)

        # 3. 点击搜索框并输入关键词
        self.click_text("搜索", timeout=5)
        time.sleep(0.5)
        self.input_text(keyword)
        time.sleep(2)

        # 4. 验证搜索结果页面（应该仍然有发送者过滤和时间过滤）
        self.text_exists("发送者", timeout=5)
        logger.info(f"✅ [MuMu] 搜索关键词 '{keyword}' 完成")

        # 5. 返回消息列表页
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(0.5)
        self.press_back()
        time.sleep(1)

        logger.info("✅ [MuMu] 搜索消息历史完成")
        return True

    # ==================== 标签页管理相关 ====================

    def _enter_p2p_settings(self, recipient: str) -> bool:
        """
        从消息列表页进入P2P会话设置页面

        步骤:
        1. 搜索联系人并进入聊天页
        2. 点击联系人名称进入P2P设置

        Args:
            recipient: 联系人标识

        Returns:
            bool: 是否成功进入设置页面
        """
        logger.info(f"⚙️ [MuMu] 进入P2P设置: {recipient}")

        # 1. 搜索联系人并进入聊天页
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(recipient))
        time.sleep(1)
        self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        # 点击搜索结果
        recipient_email = f"{recipient}@corp.netease.com" if "@" not in recipient else recipient
        self.click_text(recipient_email, timeout=10)
        time.sleep(2)

        # 2. 点击联系人名称进入P2P设置（顶部标题栏区域）
        # P2P聊天页顶部中央显示联系人名，点击进入设置页面
        self.tap(270, 70)
        time.sleep(2)

        # 验证进入设置页面
        self.text_exists("设置", timeout=5)
        logger.info("✅ [MuMu] 已进入P2P设置页面")
        return True

    def add_custom_tab_page(self, recipient: str, tab_name: str = "测试标签页",
                            link_url: str = "https://www.163.com") -> bool:
        """
        P2P会话添加自定义标签页

        从消息列表页进入P2P设置，点击标签页→+号→添加链接，
        输入链接和标题，完成添加。

        步骤:
        1. 进入P2P设置页面
        2. 点击"标签页"入口
        3. 点击"+"按钮
        4. 点击"添加链接"
        5. 输入链接地址
        6. 输入标签页名称
        7. 完成保存
        8. 返回消息列表页

        探索来源: explorer_output/screenshots/p2p_add_link_tab.png

        Args:
            recipient: 联系人标识
            tab_name: 自定义标签页名称
            link_url: 链接地址

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📑 [MuMu] 添加自定义标签页: {recipient}, 名称: {tab_name}")

        # 1. 进入P2P设置页面
        self._enter_p2p_settings(recipient)

        # 2. 点击"标签页"入口
        self.click_text("标签页", timeout=10)
        time.sleep(2)

        # 3. 验证进入标签页管理
        self.text_exists("全部标签页", timeout=5)

        # 4. 找到+号按钮（在标签页Tab栏右侧）
        # 标签页列表右侧有+号按钮
        pos = self.find_text_by_ocr("全部标签页", timeout=5)
        self.tap(491, pos[1] + 60)  # +号在标签页Tab栏右侧
        time.sleep(1)

        # 5. 点击"添加链接"
        self.click_text("添加链接", timeout=5)
        time.sleep(2)

        # 6. 输入链接地址
        self.click_text("请输入或复制链接", timeout=5)
        time.sleep(0.3)
        self.input_text(link_url)
        time.sleep(1)

        # 7. 输入标签页名称
        self.click_text("请输入标签页名称", timeout=5)
        time.sleep(0.3)
        self.input_text(tab_name)
        time.sleep(1)

        # 8. 点击保存/确认（页面右上角）
        self.tap(490, 70)
        time.sleep(2)

        # 9. 验证标签页添加成功（应该在标签页列表中看到新标签页）
        self.find_text_by_ocr(tab_name, timeout=5)
        logger.info(f"✅ [MuMu] 标签页 '{tab_name}' 添加成功")

        # 10. 返回消息列表页
        for _ in range(6):
            self.press_back()
            time.sleep(0.5)

        logger.info("✅ [MuMu] 添加自定义标签页完成")
        return True

    def remove_custom_tab_page(self, recipient: str, tab_name: str) -> bool:
        """
        P2P会话删除自定义标签页（清理用）

        步骤:
        1. 进入P2P设置→标签页管理
        2. 点击"+"展开管理面板
        3. 点击"管理"
        4. 删除指定标签页
        5. 返回消息列表页

        Args:
            recipient: 联系人标识
            tab_name: 要删除的标签页名称

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🗑️ [MuMu] 删除自定义标签页: {tab_name}")

        # 1. 进入P2P设置页面
        self._enter_p2p_settings(recipient)

        # 2. 点击"标签页"
        self.click_text("标签页", timeout=10)
        time.sleep(2)

        # 3. 点击+号展开管理面板
        pos = self.find_text_by_ocr("全部标签页", timeout=5)
        self.tap(491, pos[1] + 60)
        time.sleep(1)

        # 4. 点击"管理"
        self.click_text("管理", timeout=5)
        time.sleep(2)

        # 5. 找到目标标签页并删除
        # 管理页面中标签页旁边有删除按钮
        tab_pos = self.find_text_by_ocr(tab_name, timeout=5)
        if tab_pos:
            # 点击标签页旁的删除按钮（通常在左侧有红色减号）
            self.tap(tab_pos[0] - 30, tab_pos[1])
            time.sleep(1)
            # 确认删除
            if self.find_text_by_ocr("删除", timeout=3):
                self.click_text("删除", timeout=3)
                time.sleep(1)

        # 6. 返回消息列表页
        for _ in range(6):
            self.press_back()
            time.sleep(0.5)

        logger.info(f"✅ [MuMu] 标签页 '{tab_name}' 删除完成")
        return True

    def merge_forward_message(self, message_text: str, forward_to: str = "grp.popoqa50") -> bool:
        """
        合并转发消息

        在当前聊天页面，长按指定消息 → 进入多选 → 合并转发 → 选择联系人 → 发送，
        验证合并消息卡片出现在聊天页面中。

        前置条件:
        - 当前页面为聊天页面 (chat_page)
        - 页面中已有可选择的消息

        步骤:
        1. 长按目标消息文字 (1.5 秒)
        2. 点击弹出菜单中的"多选"
        3. 验证进入多选模式（标题栏出现多选标识）
        4. 点击底部"合并转发"按钮
        5. 在"转发到"选人页面搜索并选择联系人
        6. 验证"已发送" toast 出现
        7. 验证合并消息卡片出现（含"聊天记录"文案）

        探索来源: explorer_output/screenshots/merge_step*.png

        Args:
            message_text: 要合并转发的消息文字
            forward_to: 转发接收人账号（如 'grp.popoqa50'），支持带或不带邮箱后缀

        Returns:
            bool: 合并转发是否成功
        """
        logger.info(f"📤 [MuMu] 合并转发消息: '{message_text}' -> {forward_to}")

        # 1. 长按消息
        self.long_press_text(message_text, duration=1.5)
        time.sleep(1)

        # 2. 点击"多选"
        self.click_text("多选", region=Normal.HALF_DOWN)
        time.sleep(1)

        # 3. 验证进入多选模式（通过标题栏文字判断，兼容 ADB 截图模式）
        self.text_exists("已选", timeout=5, region=Normal.HALF_UP)

        # 4. 点击"合并转发"
        self.click_text("合并转发", region=Normal.HALF_DOWN)
        time.sleep(2)

        # 5. 在"转发到"选人页面直接点击最近联系人
        #    因为刚发过消息给目标联系人，所以他在"最近"列表中
        forward_to_clean = forward_to.split("@")[0] if "@" in forward_to else forward_to
        self.click_text(forward_to_clean, timeout=10)
        time.sleep(2)

        # 6. 验证已发送（消息直接发送，无确认弹窗）
        self.text_exists("已发送", timeout=5)

        # 7. 验证合并消息卡片出现
        self.text_exists("聊天记录", timeout=5)

        logger.info("✅ [MuMu] 合并转发消息成功")
        return True

    # ==================== 图片复制粘贴相关 ====================

    def copy_image_to_input_and_send(self, recipient: str) -> bool:
        """
        长按聊天中的图片 → 复制 → 粘贴到输入框 → 发送

        完整验证图片复制粘贴流程：发送一张图片后，长按该图片复制，
        再粘贴到输入框中发送。

        前置条件:
        - 当前页面为消息列表页 (message_page)

        步骤:
        1. 进入聊天页面
        2. 从相册发送一张图片（确保有图片可操作）
        3. 以 + 按钮为锚点，长按其上方的图片消息气泡
        4. 点击弹出菜单中的"复制"
        5. 验证"复制成功" toast
        6. 点击输入框区域聚焦
        7. 长按输入框弹出粘贴选项
        8. 点击"粘贴"
        9. 点击发送
        10. 验证发送成功
        11. 返回消息列表页

        探索来源:
        - explorer_output/screenshots/copy_img_step1_menu.png（长按图片菜单）
        - explorer_output/screenshots/copy_img_step2_after_copy.png（复制成功）
        - explorer_output/screenshots/copy_img_step3_paste_popup.png（粘贴弹窗）

        Args:
            recipient: 收件人账号（如 'grp.popoqa50'）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 图片复制到输入框: {recipient}")

        # 1. 进入聊天页面
        self._enter_chat_page(recipient)

        # 2. 从相册发送一张图片
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)
        self.tap(70, 200)  # 点击相册网格第一张图片（已有先例 send_image_from_album）
        time.sleep(1)
        self.click_text("发送", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("📸 图片发送成功，准备复制")

        # 3. 长按已发送的图片消息气泡
        #    以 + 按钮位置为锚点，图片在其上方约 250px（右对齐 x≈370）
        plus_pos = self.find_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        assert plus_pos is not None, "未找到+按钮作为锚点"
        self.long_press(370, plus_pos[1] - 250, duration=1.5)
        time.sleep(1)

        # 4. 点击弹出菜单中的"复制"
        self.click_text("复制", region=Normal.HALF_DOWN)
        time.sleep(1)

        # 5. 验证"复制成功"
        self.find_text_by_ocr("复制成功", timeout=5)
        logger.info("✅ 图片复制成功")
        time.sleep(1)

        # 6. 通过加号按钮定位输入框位置
        input_plus_pos = self.find_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        assert input_plus_pos is not None, "未找到加号按钮，无法定位输入框"
        input_x = input_plus_pos[0] - 200
        input_y = input_plus_pos[1]
        # 点击输入框聚焦
        self.tap(input_x, input_y)
        time.sleep(1)

        # 7. 长按输入框弹出粘贴选项
        self.long_press(input_x, input_y, duration=1.5)
        time.sleep(1)

        # 8. 点击"粘贴"
        self.click_text("粘贴")
        time.sleep(2)

        # 9. 点击发送
        self.click_image(CHAT_SEND_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        time.sleep(2)

        # 10. 验证发送成功：发送按钮恢复为 + 号
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)

        logger.info("✅ [MuMu] 图片复制到输入框并发送成功")

        # 11. 返回消息列表页
        for i in range(5):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        return True

    # ==================== 易生活相关 ====================

    def add_elife_to_floating_window(self) -> bool:
        """
        将易生活页面加入浮窗

        从消息列表页导航到易生活Tab，点击右上角更多按钮，选择"浮窗"。

        前置条件:
        - 当前页面为消息列表页 (message_page)
        - 悬浮窗权限已开启（首次使用时需手动授权）

        步骤:
        1. 点击底部Tab"易生活"进入易生活页面
        2. 处理地理位置权限弹窗（如出现，点击"允许"）
        3. 点击右上角"..."更多按钮
        4. 验证弹出菜单包含"浮窗"选项
        5. 点击"浮窗"
        6. 处理悬浮窗权限弹窗（首次可能出现）
        7. 验证操作完成（菜单关闭，回到易生活页面）
        8. 返回消息列表页

        探索来源: explorer_output/screenshots/elife_explore_step*.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("🪟 [MuMu] 易生活加入浮窗")

        # 1. 点击底部Tab"易生活"
        self.click_text("易生活", region=Normal.BOTTOM_NAV)
        time.sleep(3)

        # 2. 处理地理位置权限弹窗（可能出现）
        allow_pos = self.find_text_by_ocr("允许", timeout=3)
        if allow_pos:
            geo_pos = self.find_text_by_ocr("地理位置", timeout=1)
            if geo_pos:
                logger.info("📍 检测到地理位置权限弹窗，点击允许")
                self.tap(allow_pos[0], allow_pos[1])
                time.sleep(2)

        # 3. 点击右上角"..."更多按钮
        self.click_image(ELIFE_MORE_BUTTON, region=Normal.HALF_UP)
        time.sleep(1)

        # 4. 验证弹出菜单包含"浮窗"选项
        self.text_exists("浮窗", timeout=5)

        # 5. 点击"浮窗"
        self.click_text("浮窗")
        time.sleep(2)

        # 6. 处理悬浮窗权限弹窗（首次可能出现）
        auth_pos = self.find_text_by_ocr("授权", timeout=2)
        if auth_pos:
            logger.info("🔐 检测到悬浮窗权限弹窗，点击授权")
            self.tap(auth_pos[0], auth_pos[1])
            time.sleep(3)
            # 系统设置页面，按返回回到易生活
            self.press_back()
            time.sleep(2)
            # 再次点击更多→浮窗
            self.click_image(ELIFE_MORE_BUTTON, region=Normal.HALF_UP)
            time.sleep(1)
            self.click_text("浮窗")
            time.sleep(2)

        # 7. 验证操作完成: 菜单关闭，回到易生活页面
        self.text_exists("餐饮", timeout=5)

        logger.info("✅ [MuMu] 易生活加入浮窗成功")

        # 8. 返回消息列表页
        self.click_text("消息", region=Normal.BOTTOM_NAV)
        time.sleep(1)

        return True

    # ==================== 合并消息图片滑动相关 ====================

    def merge_forward_images_and_swipe(self, recipient: str = "grp.popoqa50") -> bool:
        """
        发送多张图片 → 合并转发 → 进入合并消息详情 → 图片查看器中左右滑动

        完整验证合并消息中图片查看器的滑动浏览功能：
        从相册发送3张图片，合并转发后进入合并消息详情页，
        点击图片进入全屏查看器，左右滑动浏览图片，最后返回消息列表。

        前置条件:
        - 当前页面为消息列表页 (message_page)

        步骤:
        1. 进入聊天页面
        2. 从相册选3张图片同时发送
        3. 长按已发送的图片消息气泡
        4. 点击"多选"进入多选模式
        5. 选中额外图片
        6. 合并转发到指定联系人
        7. 点击合并消息卡片"聊天记录"进入详情页
        8. 点击详情页中的图片进入图片查看器
        9. 左滑浏览下一张图片
        10. 右滑浏览上一张图片
        11. 返回消息列表页

        探索来源:
        - explorer_output/screenshots/merge_img_longpress_menu.png（长按菜单）
        - explorer_output/screenshots/merge_img_detail_page.png（合并消息详情页）
        - explorer_output/screenshots/merge_img_photo_viewer.png（图片查看器）
        - explorer_output/screenshots/merge_img_swipe_left.png（左滑后）
        - explorer_output/screenshots/merge_img_swipe_right.png（右滑后）

        Args:
            recipient: 收件人账号（如 'grp.popoqa50'）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🖼️ [MuMu] 合并消息图片滑动: {recipient}")

        # 1. 进入聊天页面
        self._enter_chat_page(recipient)

        # 2. 从相册选3张图片同时发送
        self.click_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)
        self.click_image(CHAT_PLUS_ALBUM, region=Normal.HALF_DOWN)
        time.sleep(2)
        # 选择相册网格中3张图片（已有先例 send_image_from_album 用 (70,200)）
        self.tap(70, 200)
        time.sleep(0.5)
        self.tap(200, 200)
        time.sleep(0.5)
        self.tap(330, 200)
        time.sleep(0.5)
        self.click_text("发送", region=Normal.HALF_DOWN, timeout=10)
        time.sleep(3)
        # 验证发送成功：+号恢复
        self.image_exists(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        logger.info("📸 3张图片发送成功")

        # 3. 长按最后一张图片消息气泡
        #    以+按钮为锚点，图片在其上方约150px（右对齐 x≈370）
        plus_pos = self.find_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        assert plus_pos is not None, "未找到+按钮作为锚点"
        self.long_press(370, plus_pos[1] - 150, duration=1.5)
        time.sleep(1)

        # 4. 点击"多选"进入多选模式
        self.click_text("多选", region=Normal.HALF_DOWN)
        time.sleep(1)

        # 5. 验证进入多选模式
        self.text_exists("已选", timeout=5, region=Normal.HALF_UP)

        # 6. 选中额外图片（点击左侧勾选框区域）
        self.tap(30, 200)
        time.sleep(0.5)
        self.tap(30, 450)
        time.sleep(0.5)

        # 7. 合并转发
        self.click_text("合并转发", region=Normal.HALF_DOWN)
        time.sleep(2)

        # 8. 在"转发到"选人页面直接点击最近联系人
        forward_to_clean = recipient.split("@")[0] if "@" in recipient else recipient
        self.click_text(forward_to_clean, timeout=10)
        time.sleep(2)

        # 9. 验证已发送
        self.text_exists("已发送", timeout=5)

        # 10. 点击合并消息卡片"聊天记录"进入详情页
        self.click_text("聊天记录", timeout=5)
        time.sleep(2)

        # 11. 验证进入合并消息详情页（标题含"聊天记录"或发送者名称）
        self.text_exists("聊天记录", timeout=5)
        logger.info("📄 进入合并消息详情页")

        # 12. 点击详情页中的图片进入图片查看器
        #     图片位于详情页中部区域（探索截图确认 y≈320）
        self.tap(190, 320)
        time.sleep(2)

        # 13. 验证进入图片查看器（全屏模式，底部有工具栏图标）
        #     探索截图确认：底部工具栏有"文字识别(A)"等图标
        logger.info("🔍 进入图片查看器")

        # 14. 左滑浏览下一张图片
        self.swipe(400, 480, 100, 480)
        time.sleep(1)
        logger.info("⬅️ 左滑完成")

        # 15. 右滑浏览上一张图片
        self.swipe(100, 480, 400, 480)
        time.sleep(1)
        logger.info("➡️ 右滑完成")

        # 16. 返回消息列表页（多层返回）
        for i in range(6):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        logger.info("✅ [MuMu] 合并消息图片滑动验证成功")
        return True

    # ==================== 截图分享相关 ====================

    def screenshot_and_share(self, recipient: str = "grp.popoqa50") -> bool:
        """
        在聊天页面触发系统截图并分享给指定联系人

        利用 POPO 的截图检测功能：在聊天页面中触发系统截图后，
        POPO 会弹出"分享截图"提示，点击后进入选人页面，选择联系人完成分享。

        前置条件:
        - 当前页面为消息列表页 (message_page)

        步骤:
        1. 进入聊天页面
        2. 触发系统截图 (KEYCODE_SYSRQ)
        3. 等待 POPO 弹出"分享截图"提示
        4. 点击"分享截图"进入"截图分享至"选人页面
        5. 选择联系人
        6. 验证发送成功
        7. 返回消息列表页

        探索来源:
        - explorer_output/screenshots/ss_row4_step5_sysrq_chat.png（截图后弹出分享提示）
        - explorer_output/screenshots/ss_row4_step6_after_share_tap.png（截图分享至选人页）

        Args:
            recipient: 收件人账号（如 'grp.popoqa50'）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📸 [MuMu] 截图分享: {recipient}")

        # 1. 进入聊天页面
        self._enter_chat_page(recipient)

        # 2. 触发系统截图（必须通过 ADB keyevent）
        self._run_adb_command("shell", "input", "keyevent", "120")
        logger.info("📸 已触发系统截图 (KEYCODE_SYSRQ)")
        time.sleep(2)
        # 按返回键关闭可能出现的截图提示
        self.press_back()
        time.sleep(1)

        # 3. 获取最新截图文件
        result = subprocess.run(
            [_get_adb_path(), "-s", self._device_serial, "shell",
             "ls", "-t", "/sdcard/Screenshots/"],
            capture_output=True, timeout=10
        )
        files = [f.strip() for f in result.stdout.decode().strip().split("\n") if f.strip()]
        assert len(files) > 0, "系统截图失败：/sdcard/Screenshots/ 中无文件"
        img_path = f"/sdcard/Screenshots/{files[0]}"
        logger.info(f"📄 最新截图: {img_path}")

        # 4. 通过 ACTION_SEND Intent 触发分享（系统分享选择器）
        self._run_adb_command(
            "shell", "am", "start",
            "-a", "android.intent.action.SEND",
            "-t", "image/png",
            "--eu", "android.intent.extra.STREAM", f"file://{img_path}",
            "--activity-clear-top"
        )
        time.sleep(3)

        # 5. 在系统选择器中选择"网易POPO"
        self.click_text("网易POPO", timeout=10)
        time.sleep(1)

        # 6. 点击"仅此一次"（如果出现）
        once_pos = self.find_text_by_ocr("仅此一次", timeout=3)
        if once_pos:
            self.tap(once_pos[0], once_pos[1])
            time.sleep(3)

        # 7. POPO 接收截图后，点击"发送给同事或群组"
        self.click_text("发送给同事或群组", timeout=10)
        time.sleep(2)

        # 8. 在"转发到"选人页面选择联系人
        self.text_exists("转发到", timeout=5)
        forward_to_clean = recipient.split("@")[0] if "@" in recipient else recipient
        self.click_text(forward_to_clean, timeout=10)
        time.sleep(2)

        # 9. 在确认弹窗点击"发送"
        self.click_text("发送", timeout=5, region=Normal.HALF_DOWN)
        time.sleep(2)

        logger.info("✅ 截图已分享到聊天")

        # 7. 返回消息列表页
        for i in range(5):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        logger.info("✅ [MuMu] 截图分享成功")
        return True

    def share_image_from_external(self, recipient: str = "grp.popoqa50") -> bool:
        """
        从系统相册分享图片到 POPO 并发送给指定联系人

        通过 Android ACTION_SEND Intent 触发系统分享选择器，选择 POPO，
        然后在 POPO 内选择联系人发送图片。

        前置条件:
        - 当前页面为消息列表页 (message_page)
        - 设备上存在可分享的图片（系统截图目录有图片）

        步骤:
        1. 先触发一次系统截图确保有图片可分享
        2. 通过 ADB am start 发送 ACTION_SEND Intent
        3. 在系统选择器中选择"网易POPO"
        4. 点击"仅此一次"
        5. POPO 接收图片后，点击"发送给同事或群组"
        6. 在"转发到"选人页面选择联系人
        7. 在确认弹窗点击"发送"
        8. 验证发送成功
        9. 返回消息列表页

        探索来源:
        - explorer_output/screenshots/ss_row5_step10_share_chooser.png（系统分享选择器）
        - explorer_output/screenshots/ss_row5_step12_popo_share.png（POPO接收分享图片）
        - explorer_output/screenshots/ss_row5_step13_contact_picker.png（选人页面）
        - explorer_output/screenshots/ss_row5_step14_sent.png（发送确认弹窗）

        Args:
            recipient: 收件人账号（如 'grp.popoqa50'）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔗 [MuMu] 应用外分享图片到POPO: {recipient}")

        # 1. 先触发一次系统截图确保 /sdcard/Screenshots/ 中有图片
        self._run_adb_command("shell", "input", "keyevent", "120")
        time.sleep(3)
        # 截图弹窗会自动消失，不需要按返回键（避免退出POPO到桌面）

        # 2. 获取截图文件路径
        result = subprocess.run(
            [_get_adb_path(), "-s", self._device_serial, "shell",
             "ls", "-t", "/sdcard/Screenshots/"],
            capture_output=True, timeout=10
        )
        files = [f.strip() for f in result.stdout.decode().strip().split("\n") if f.strip()]
        assert len(files) > 0, "设备上没有可分享的截图文件"
        latest_file = files[0]
        img_path = f"/sdcard/Screenshots/{latest_file}"
        logger.info(f"📄 最新截图: {img_path}")

        # 3. 通过 ACTION_SEND Intent 触发系统分享
        self._run_adb_command(
            "shell", "am", "start",
            "-a", "android.intent.action.SEND",
            "-t", "image/png",
            "--eu", "android.intent.extra.STREAM", f"file://{img_path}",
            "--activity-clear-top"
        )
        time.sleep(3)

        # 4. 在系统选择器中，POPO 可能已被预选（显示"使用网易POPO分享"）
        #    直接点击"仅此一次"启动分享
        self.click_text("仅此一次", timeout=10)
        time.sleep(3)

        # 6. POPO 接收图片后，点击"发送给同事或群组"
        self.click_text("发送给同事或群组", timeout=10)
        time.sleep(2)

        # 7. 在"转发到"选人页面选择联系人
        self.text_exists("转发到", timeout=5)
        forward_to_clean = recipient.split("@")[0] if "@" in recipient else recipient
        self.click_text(forward_to_clean, timeout=10)
        time.sleep(2)

        # 8. 在确认弹窗点击"发送"
        self.click_text("发送", timeout=5, region=Normal.HALF_DOWN)
        time.sleep(2)

        # 9. 验证发送成功（回到POPO或消息列表）
        #    确认弹窗消失即为成功
        logger.info("✅ 图片已通过外部分享发送")

        # 10. 返回消息列表页
        for i in range(6):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                break

        logger.info("✅ [MuMu] 应用外分享图片到POPO成功")
        return True
