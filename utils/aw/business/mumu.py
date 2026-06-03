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
from utils.aw.search_region import Normal, Search

logger = logging.getLogger(__name__)

POPO_PACKAGE = "com.netease.popo"
POPO_ACTIVITY = "com.netease.popo.MainActivity"


class POPOLoginRequired(Exception):
    """open_app() 检测到登录页时抛出，由 UsersFactory 捕获后自动重登"""
    pass


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
        """通过 ADB monkey 命令启动 POPO 应用（不依赖桌面图标图片）"""
        logger.info("📱 [MuMu] 通过 ADB 启动 POPO...")
        self._run_adb_command("shell", "monkey", "-p", POPO_PACKAGE,
                              "-c", "android.intent.category.LAUNCHER", "1")
        self.sleep(5)

    def stop_app(self, package: str = POPO_PACKAGE) -> bool:
        """停止应用，返回 True 表示 App 已处于停止状态"""
        logger.info(f"📱 正在停止应用 {package}...")
        return self._run_adb_command("shell", "am", "force-stop", package)

    # ==================== 页面导航 (MuMu 特定) ====================

    def go_to_contacts(self) -> bool:
        """
        导航到通讯录页面

        MuMu 端: 底部"更多"Tab → "通讯录"
        """
        logger.info("📇 [MuMu] 进入通讯录页面")
        self.click_text("更多", timeout=5)
        time.sleep(0.5)
        return self.click_text("通讯录", timeout=5)
        time.sleep(0.5)
        logger.info("✅ 应用已停止")
        return True

    def _is_popo_foreground(self) -> bool:
        """ADB 检测 POPO 是否在前台（mCurrentFocus 行包含包名）"""
        try:
            result = self.driver._adb("shell", "dumpsys", "window", "windows")
            if result is None or result.returncode != 0:
                return False
            for line in result.stdout.decode("utf-8", errors="ignore").splitlines():
                if "mCurrentFocus" in line and POPO_PACKAGE in line:
                    return True
            return False
        except Exception:
            return False

    def _is_popo_running(self) -> bool:
        """ADB 检测 POPO 进程是否存在"""
        try:
            result = self.driver._adb("shell", "pidof", POPO_PACKAGE)
            if result is None:
                return False
            return bool(result.stdout.decode("utf-8", errors="ignore").strip())
        except Exception:
            return False

    def open_app(self):
        """
        启动 POPO 并等待进入消息列表首页

        流程：
        1. ADB 判断 POPO 是否运行 + 是否在前台
        2. 在前台 → 图片判断当前页面（消息页/登录页/其他）
        3. 未在前台（进程存在但被切走）→ force-stop 后重启
        4. 未运行 → 直接冷启动
        """
        logger.info("📱 [MuMu] 启动 POPO 应用...")
        self.driver.focus_window()
        self.sleep(0.3)

        # ── Step 1: ADB 判断运行状态 ──────────────────────────────
        popo_running = self._is_popo_running()
        popo_in_fg = self._is_popo_foreground() if popo_running else False

        logger.info(f"  POPO 进程: {'运行中' if popo_running else '未运行'} | "
                    f"前台: {'是' if popo_in_fg else '否'}")

        # ── Step 2: 在前台 → 图片判断当前页面 ────────────────────
        if popo_in_fg:
            if self.find_image(MESSAGE_TAB_MSG_TEXT, timeout=2):
                logger.info("✅ [MuMu] POPO 已在消息列表页，无需启动")
                self.pop_not_allowed()
                return
            if self.find_image(LOGIN_POPO_TEXT, timeout=1):
                logger.warning("⚠️ [MuMu] POPO 在前台但处于登录页，登录态丢失")
                raise POPOLoginRequired("POPO 在前台但处于登录页，登录态已丢失")
            # 在前台但在其他深层页面 → force-stop 重启更稳
            logger.info("⚠️ [MuMu] POPO 在前台但不在消息页，force-stop 后重启")
            self.stop_app()
            self.sleep(0.5)

        # ── Step 3: 进程存在但不在前台 → force-stop 再启 ─────────
        elif popo_running:
            logger.info("⚠️ [MuMu] POPO 进程存在但不在前台，force-stop 后重启")
            self.stop_app()
            self.sleep(0.5)

        # ── Step 4: 冷启动 ────────────────────────────────────────
        self.start_app()
        self.sleep(2)

        for _ in range(8):
            self.sleep(1)
            self.pop_not_allowed()
            if self.find_image(MESSAGE_TAB_MSG_TEXT, timeout=1):
                self.pop_not_allowed()
                logger.info("✅ [MuMu] POPO 已启动，已进入消息列表页")
                return
            if self.find_image(LOGIN_POPO_TEXT, timeout=1):
                logger.warning("⚠️ [MuMu] 启动后检测到登录页，登录态丢失")
                raise POPOLoginRequired("POPO 启动后落在登录页，登录态已丢失")

        # 超时兜底
        self.image_exists(MESSAGE_TAB_MSG_TEXT, timeout=5, region=Normal.HALF_UP)
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

        # 快速检查：如果已在消息列表页（force-stop 后重启保留了登录态），跳过登录
        # 用左上角"消息"文案图片判断，比底部 Tab 图片更稳定（不受未读消息状态影响）
        # 同时保留底部 Tab region 检查作为备用
        _TAB_REGION = (0, 700, 540, 260)
        if (self.find_image(MESSAGE_TAB_MSG_TEXT, timeout=2)
                or self.find_image(MESSAGE_TAB_BLUE, timeout=2, region=_TAB_REGION)):
            logger.info("✅ [MuMu] 已登录状态，跳过登录步骤")
            self.pop_not_allowed()
            return

        # 4. 输入邮箱：点击邮箱输入框 → 清空 → 输入新邮箱
        #    不管输入框是空的（显示"输入邮箱"占位符）还是保留了旧邮箱，都先清空再输入
        #    页面布局: "邮箱"Tab y≈313, 邮箱输入框 y≈405, 密码输入框 y≈500
        #    用 dy=92 从"邮箱"Tab 偏移到邮箱输入框
        self.click_text("邮箱", timeout=3, dx=50, dy=92)
        self.sleep(0.5)
        # 清空输入框（通过 ADB keyevent 删除）
        self._clear_input_field()
        self.sleep(0.1)
        self.input_text(str(uid))
        logger.info(f"📧 已输入邮箱: {uid}")

        # 5. 输入密码：直接 OCR 找"输入密码"占位文字点击，避免偏移计算在并行时失效
        #    重试2次：首次点击可能因焦点问题无效
        for _attempt in range(2):
            pwd_pos = self.find_text_by_ocr("输入密码", timeout=3)
            if pwd_pos:
                self.tap(pwd_pos[0], pwd_pos[1])
            else:
                # 占位符不可见（已有内容），用偏移兜底
                self.click_text("邮箱", timeout=3, dx=50, dy=187)
            self.sleep(0.3)
            self._clear_input_field()
            self.sleep(0.2)
            self.input_text(str(password))
            self.sleep(0.5)
            # 验证密码已输入：占位符应已消失
            still_placeholder = self.find_text_by_ocr("输入密码", timeout=1)
            if still_placeholder is None:
                break  # 密码成功输入
            logger.warning(f"⚠️ 密码输入可能未生效（第{_attempt+1}次），重试")
        logger.info("🔑 已输入密码")
        # 不按返回键收起键盘，避免部分模拟器版本中按返回键退出登录页面
        # 步骤6和7会独立查找勾选框和登录按钮图片，超时后会自动重试

        # 6. 勾选协议（先检查未勾选状态，如果未找到说明已勾选）
        if self.find_image(LOGIN_READ_CENTER_FALSE, timeout=1):
            self.click_image(LOGIN_READ_CENTER_FALSE)
            self.sleep(0.1)
            logger.info("☑️ 已勾选协议")
        else:
            logger.info("☑️ 协议已是勾选状态，无需再勾选")

        # 7. 点击登录按钮
        self.click_image(LOGIN_ENTER)

        # 8. 等待进入消息列表页，期间可能弹出权限授权弹窗
        for _ in range(5):
            self.sleep(1)
            # 处理可能出现的弹窗（悬浮窗权限、联系人同步授权等）
            try:
                self.pop_not_allowed()
            except Exception:
                pass
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1, region=_TAB_REGION):
                break
        else:
            # 最后一次尝试：直接断言图片存在
            self.image_exists(MESSAGE_TAB_BLUE, timeout=1)

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

        # 场景3: 连续按返回可能退出到了桌面，ADB 重启App
        logger.warning("⚠️ 连续5次返回未找到消息页，通过 ADB 重启App")
        self.stop_app()
        time.sleep(1)
        self.start_app()
        time.sleep(3)
        if self.find_image(MESSAGE_TAB_BLUE, timeout=10):
            logger.info("✅ 重启App后成功回到消息列表页")
            return True
        if self.find_image(LOGIN_POPO_TEXT, timeout=3):
            logger.info("📱 重启App后到达登录页，无需退登")
            return False

        # 最后的兜底: 再次尝试强制停止并重启
        logger.warning("⚠️ 首次重启未成功，再次尝试...")
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
        # 处理登录后可能出现的联系人同步/授权弹窗（OCR方式补充检测）
        elif self.find_text_by_ocr("授权", timeout=1) and \
                self.find_text_by_ocr("取消", timeout=0.5):
            if not isallow:
                self.click_text("取消", timeout=2)
                logger.info("授权弹窗已取消")
            else:
                self.click_text("授权", timeout=2)
                logger.info("授权弹窗已同意")
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

        # 使用 _ensure_message_page 确保回到消息列表（会自动处理桌面/深层页面等场景）
        self._ensure_message_page()
        time.sleep(0.5)

        # 关闭可能遮挡的 + 菜单
        if self.find_text_by_ocr("创建群组", timeout=1):
            logger.info("⚠️ 检测到 + 菜单，先关闭")
            self.press_back()
            time.sleep(0.5)

        # 方案1：图片匹配（兼容旧模板）
        matched = self.find_image(SESSION_GROUP_MORE_BUTTON, timeout=2)
        if matched:
            self.tap(matched[0], matched[1])
        else:
            # 方案2：坐标直接点击 ≡ 按钮（tab 行最右侧，x≈505, y≈277）
            logger.info("⚠️ SESSION_GROUP_MORE_BUTTON 图片未匹配，使用坐标 (505, 277)")
            self.tap(505, 277)
        time.sleep(1.5)  # 等待面板动画

        # 验证面板已打开（超时6s，给 OCR 更多时间）
        pos = self.find_text_by_ocr("会话分组", timeout=6)
        if pos is None:
            logger.warning("⚠️ 第一次点击后未发现'会话分组'，重试坐标 (505, 277)")
            self.tap(505, 277)
            time.sleep(2)
            pos = self.find_text_by_ocr("会话分组", timeout=6)

        assert pos is not None, "会话分组弹窗打开失败：OCR 未找到'会话分组'"
        logger.info("✅ 会话分组弹窗已打开")
        return True

    def close_session_group_panel(self) -> bool:
        """
        关闭展开的会话分组弹窗（点击蒙层区域或按返回键）

        步骤:
        1. 会话分组弹窗展开后，按返回键关闭
        2. 等待面板关闭动画
        3. 验证回到消息列表页

        探索来源: explorer_output/screenshots/session_group_more.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 关闭会话分组弹窗")
        # 按返回键关闭面板（比点击蒙层更可靠）
        self.press_back()
        time.sleep(1)
        # 验证面板已关闭 - 消息列表页底部导航栏可见
        self.image_exists(MESSAGE_TAB_BLUE, timeout=5)
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
        # "管理"按钮在面板右上角，优先 OCR 找文字位置
        pos = self.find_text_by_ocr("管理", timeout=5)
        if pos is None:
            logger.warning("⚠️ OCR 未找到'管理'，尝试点击右上角固定坐标 (490, 330)")
            self.tap(490, 330)
        else:
            self.tap(pos[0], pos[1])
        time.sleep(1)
        # 兼容页面标题为"管理分组"或"分组管理"
        ok = self.find_text_by_ocr("管理分组", timeout=4)
        if ok is None:
            ok = self.find_text_by_ocr("分组管理", timeout=3)
        if ok is None:
            ok = self.find_text_by_ocr("分组", timeout=3)
        assert ok is not None, "未进入管理分组页面（OCR 未找到'管理分组'/'分组管理'/'分组'）"
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
        self.text_exists("隐藏", timeout=5)
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
        self.text_exists("展示", timeout=5)

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

    def switch_session_group_tab(self, tab_name: str) -> bool:
        """
        切换会话分组Tab标签

        步骤:
        1. 在消息列表页的分组标签栏中，点击目标Tab名称
        2. 等待列表刷新

        探索来源: explorer_output/screenshots/m3_tab_atme.png

        Args:
            tab_name: Tab名称，如"最近"、"@我"、"未读"、"待处理"、"单聊"、"群组"
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 切换到分组Tab: {tab_name}")
        self.click_text(tab_name, timeout=5, region=(0, 275, 540, 45))
        time.sleep(1)
        logger.info(f"✅ 已切换到 '{tab_name}' Tab")
        return True

    def open_session_box(self) -> bool:
        """
        打开会话盒子页面

        步骤:
        1. 确保在消息列表页
        2. 点击"会话盒子"条目
        3. 验证进入会话盒子页面（标题栏显示"会话盒子"）

        前置条件: 消息列表中需已存在"会话盒子"条目（已有会话被添加到盒子）

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 打开会话盒子")
        self._ensure_message_page()
        time.sleep(0.5)

        self.click_text("会话盒子", timeout=5)
        time.sleep(1.5)
        self.text_exists("会话盒子", timeout=5)
        logger.info("✅ 已进入会话盒子页面")
        return True

    def open_closed_sessions(self) -> bool:
        """
        打开关闭的会话页面

        步骤:
        1. 打开会话分组面板
        2. 点击"关闭的会话"条目
        3. 进入关闭的会话列表页

        探索来源: explorer_output/screenshots/m3_closed_sessions.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 打开关闭的会话")
        self.open_session_group_panel()
        self.click_text("关闭的会话", timeout=5)
        time.sleep(1.5)
        self.text_exists("关闭的会话", timeout=5)
        logger.info("✅ 已进入关闭的会话页面")
        return True

    def _find_menu_item(self, candidates: list, max_scrolls: int = 2) -> str:
        """
        在长按菜单中查找目标选项（支持滑动查找）

        Args:
            candidates: 候选文字列表，找到任一即返回
            max_scrolls: 最多滑动次数
        Returns:
            str: 找到的菜单项文字，未找到返回None
        """
        # 先直接查找
        for text in candidates:
            pos = self.find_text_by_ocr(text, timeout=2)
            if pos:
                return text
        # 尝试滑动菜单后查找
        for _ in range(max_scrolls):
            self.swipe(270, 900, 270, 650, duration=0.3)
            time.sleep(0.5)
            for text in candidates:
                pos = self.find_text_by_ocr(text, timeout=2)
                if pos:
                    return text
        return None

    def long_press_session_pin(self) -> bool:
        """
        长按会话列表第一个会话项，点击置顶

        步骤:
        1. 在消息列表页长按第一个会话项
        2. 在弹出菜单中点击"置顶"

        探索来源: explorer_output/screenshots/m3_longpress_scrolled.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 长按会话置顶/取消置顶")
        # 确保窗口获得焦点
        self.driver.focus_window()
        time.sleep(0.3)
        # 长按会话列表区域 - x偏右避免点到头像触发名片弹窗
        self.long_press(350, 420, duration=1.5)
        time.sleep(1)
        # 菜单中可能显示"取消置顶"或"置顶"（先匹配长的避免子串误匹配）
        target_text = self._find_menu_item(["取消置顶", "置顶"])
        if not target_text:
            # 菜单没弹出，可能是首次操作App未响应，重试
            logger.info("⚠️ 菜单未弹出，重试长按")
            self.tap(270, 300)  # 先点击一下激活页面
            time.sleep(0.5)
            self.long_press(350, 420, duration=1.5)
            time.sleep(1)
            target_text = self._find_menu_item(["取消置顶", "置顶"])
        assert target_text is not None, "未找到'置顶'或'取消置顶'选项"
        self.click_text(target_text, timeout=5)
        time.sleep(1)
        logger.info(f"✅ 会话已{target_text}")
        return True

    def long_press_session_add_to_pending(self) -> bool:
        """
        长按会话列表第一个会话项，点击添加到待处理

        步骤:
        1. 在消息列表页长按第一个会话项
        2. 在弹出菜单中点击"添加到待处理"

        探索来源: explorer_output/screenshots/m3_longpress_full.png

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 长按会话切换待处理状态")
        # 确保窗口获得焦点
        self.driver.focus_window()
        time.sleep(0.3)
        # 长按会话列表区域 - x偏右避免点到头像触发名片弹窗
        self.long_press(350, 420, duration=1.5)
        time.sleep(1)
        # 菜单中可能显示"添加到待处理"或"处理完成"，取决于当前状态
        target_text = None
        pos = self.find_text_by_ocr("添加到待处理", timeout=2)
        if pos:
            target_text = "添加到待处理"
        else:
            pos = self.find_text_by_ocr("处理完成", timeout=2)
            if pos:
                target_text = "处理完成"
        if not target_text:
            # 菜单可能需要滑动才能看到此选项
            has_menu = self.find_text_by_ocr("置顶", timeout=2) or self.find_text_by_ocr("取消置顶", timeout=1)
            if has_menu:
                self.swipe(270, 850, 270, 700, duration=0.3)
                time.sleep(0.5)
                pos = self.find_text_by_ocr("添加到待处理", timeout=2)
                if pos:
                    target_text = "添加到待处理"
                else:
                    pos = self.find_text_by_ocr("处理完成", timeout=2)
                    if pos:
                        target_text = "处理完成"
        assert target_text is not None, "未找到'添加到待处理'或'处理完成'选项"
        self.click_text(target_text, timeout=5)
        time.sleep(1)
        logger.info(f"✅ 会话已{target_text}")
        return target_text

    def long_press_session_toggle_read_status(self) -> str:
        """
        长按会话列表第一个会话项，切换已读/未读状态

        步骤:
        1. 在消息列表页长按第一个会话项
        2. 滑动菜单到下方查找"设为未读"或"设为已读"
        3. 点击找到的选项

        探索来源: explorer_output/screenshots/m3_longpress_scrolled.png

        Returns:
            str: 执行的操作 "设为未读" 或 "设为已读"
        """
        logger.info("📋 [MuMu] 长按会话切换已读/未读状态")
        # 确保窗口获得焦点
        self.driver.focus_window()
        time.sleep(0.3)
        # 长按会话列表区域 - x偏右避免点到头像触发名片弹窗
        self.long_press(350, 420, duration=1.5)
        time.sleep(1)

        # 查找"设为未读"或"设为已读"（可能需要滑动菜单）
        target_text = self._find_menu_item(["设为未读", "设为已读"])
        assert target_text is not None, "未找到'设为未读'或'设为已读'选项"
        self.click_text(target_text, timeout=5)
        time.sleep(1)
        logger.info(f"✅ 会话已{target_text}")
        return target_text

    def long_press_session_add_to_group(self, group_name: str = "") -> bool:
        """
        长按会话列表第一个会话项，点击添加至分组

        步骤:
        1. 在消息列表页长按第一个会话项
        2. 滑动菜单到下方
        3. 点击"添加至分组"
        4. 在分组选择页面选择指定分组（如有group_name参数）

        探索来源: explorer_output/screenshots/m3_longpress_scrolled.png

        Args:
            group_name: 要添加到的分组名称，为空则只打开分组选择页面
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 长按会话添加至分组: {group_name}")
        # 确保窗口获得焦点
        self.driver.focus_window()
        time.sleep(0.3)
        # 长按会话列表区域 - x偏右避免点到头像触发名片弹窗
        self.long_press(350, 420, duration=1.5)
        time.sleep(1)
        # 滑动菜单显示更多选项（添加至分组通常在菜单底部）
        target_text = self._find_menu_item(["添加至分组"])
        assert target_text is not None, "未找到'添加至分组'选项"
        self.click_text("添加至分组", timeout=5)
        time.sleep(1.5)

        if group_name:
            # 在分组选择页面点击指定分组名旁边的+号
            pos = self.find_text_by_ocr(group_name, timeout=5)
            assert pos is not None, f"未找到分组 '{group_name}'"
            # 点击分组名右侧的+号 (偏移约150px)
            self.tap(pos[0] + 150, pos[1])
            time.sleep(1)

        logger.info(f"✅ 会话已添加至分组 '{group_name}'")
        return True

    def mark_conversation_as_read(self, conversation_name: str) -> bool:
        """
        在消息列表中找到指定会话，长按它，在弹出菜单中点击"设为已读"或"设为未读"

        说明: 长按菜单中"设为已读" / "设为未读"是动态切换的——
        会话有未读消息时显示"设为已读"，已读时显示"设为未读"。
        为提高自动化稳定性，任一项都算成功（点击哪个都会触发已读/未读切换）。

        步骤:
        1. OCR 定位指定 conversation_name 在消息列表中的 y 坐标
        2. 在该 y 坐标对应的会话行上长按 (x 偏右避开头像)
        3. 通过 _find_menu_item 在弹出菜单中查找 "设为已读" 或 "设为未读"
           （_find_menu_item 内部已处理菜单 swipe-up）
        4. 点击找到的那个选项

        Args:
            conversation_name: 要操作的会话名 (如 "服务号" / "会话盒子")
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 长按会话 '{conversation_name}' → 切换已读/未读")
        # 确保窗口获得焦点
        self.driver.focus_window()
        time.sleep(0.3)

        # 1. 找到目标会话所在行
        pos = self.find_text_by_ocr(conversation_name, timeout=10)
        assert pos is not None, f"未在消息列表中找到会话 '{conversation_name}'"
        target_y = pos[1]

        # 2. 长按那条会话 (x=300 偏右避开头像)
        self.long_press(300, target_y, duration=1.5)
        time.sleep(1)

        # 3. 在弹出菜单中查找 "设为已读" 或 "设为未读"
        # _find_menu_item 内部已处理 swipe-up 滚动查找
        target_text = self._find_menu_item(["设为已读", "设为未读"])
        assert target_text is not None, (
            f"未在长按菜单中找到'设为已读'或'设为未读'选项 (会话={conversation_name})"
        )
        self.click_text(target_text, timeout=5)
        time.sleep(1)
        logger.info(f"✅ 会话 '{conversation_name}' 已{target_text}")
        return True

    def close_conversation_box(self, conversation_name: str = "会话盒子") -> bool:
        """
        关闭会话盒子

        说明: 长按"会话盒子"条目时，弹出简化菜单仅含"关闭"一项，
        不同于长按普通会话的完整菜单（无聊天预览、无可滑动项）。

        步骤:
        1. 在消息列表页找到"会话盒子"条目
        2. 长按该条目 (x=270 避开左侧头像, duration=2.0)
        3. 在弹出菜单中点击"关闭"

        Args:
            conversation_name: 会话盒子名称 (默认"会话盒子")
        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🗑️ [MuMu] 关闭会话盒子: {conversation_name}")
        self._ensure_message_page()
        time.sleep(0.5)

        # 1. 找到"会话盒子"条目
        pos = self.find_image(SESSION_BOX)
         # 2. 长按"会话盒子"条目 (简化菜单无聊天预览)
        if pos:
            self.long_press(pos[0], pos[1], duration=2.0)
            time.sleep(0.5)

            # 3. 简化菜单仅"关闭"一项，直接点击
            self.click_text("关闭", timeout=2)
            time.sleep(1)

            logger.info(f"✅ 会话盒子 '{conversation_name}' 已关闭")
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
            self.click_image(CREATE_NEW_TEAM, region=Normal.HALF_DOWN)
        except:
            pass

        time.sleep(1)
        self.text_exists(text="发起群聊", region=Normal.HALF_UP)
        self.text_exists(text="并邀请", region=Normal.HALF_UP)
        self.text_exists(text="加入群聊", region=Normal.HALF_UP)
        return True

    def delete_team(self, group_identifier: str) -> bool:
        """
        解散群组

        步骤:
        1. 进入群管理页
        2. 滑动找到"解散群组"并点击
        3. 确认解散弹窗

        Args:
            group_identifier: 群名关键词

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🗑️ 开始解散群组: {group_identifier}")
        self.enter_group_management(group_identifier)

        # 滑动查找"群管理"
        pos = None
        for screen in range(5):
            pos = self.find_text_by_ocr("群管理", timeout=1)
            if pos:
                break
            self.swipe_up(300)
            time.sleep(0.2)

        assert pos, "群管理页未找到'群管理'"
        self.tap(pos[0], pos[1])

        # 滑动查找"解散群组"
        pos = None
        for screen in range(5):
            pos = self.find_text_by_ocr("解散群组", timeout=1)
            if pos:
                break
            self.swipe_up(300)
            time.sleep(0.2)
        assert pos, "群管理页未找到'解散群组'"
        self.tap(pos[0], pos[1])

        # 确认解散弹窗
        confirm_pos = self.find_text_by_ocr("解散", timeout=3)
        if confirm_pos:
            self.tap(confirm_pos[0], confirm_pos[1])
            time.sleep(2)

        logger.info("✅ [MuMu] 群组已解散")
        return True

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
        if self.find_image(MSG_RECELL_POP, timeout=5):
            self.click_text("确定")

        # 5. 验证撤回成功（限定在原消息 Y 坐标上下 60px 范围内搜索，避免匹配到其他历史撤回记录）
        time.sleep(1)
        verify_y_top = max(0, msg_y - 60)
        verify_y_bottom = min(960, msg_y + 60)
        self.text_exists("你撤回了一条消息", timeout=5, region=(0, verify_y_top, 540, verify_y_bottom))

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
        time.sleep(0.5)

        # 2. 输入搜索关键词（SELECT_SEARCH 图片已过时，直接输入）
        self.input_text(str(recipient))
        time.sleep(1)

        # 3. 切换到对应Tab
        if is_group:
            # 大搜 Tab 标签是"群"（非"群组"），用图片匹配更稳定
            self.click_image(os.path.join(path, "搜索页面-群tab-未选中.png"),
                             region=Search.SEARCH_TAB, dy=-10)
        else:
            self.click_text("联系人", region=Normal.HALF_UP)
        time.sleep(2)

        # 4. 点击搜索结果进入聊天页
        if is_group:
            # 群搜索结果显示群名（不是 tid 数字），点结果区第一个可点元素
            # 取结果列表区第一条文字坐标并点击
            first_result = self.find_text_by_ocr(".", timeout=5, region=Search.RESULT_LIST)
            if first_result:
                self.tap(first_result[0], first_result[1])
            else:
                # 兜底：直接 tap 结果列表区中部
                self.tap(270, 300)
        else:
            # P2P：结果区域显示邮箱，用邮箱文本匹配
            recipient_email = (f"{recipient}@corp.netease.com"
                               if "@" not in recipient else recipient)
            self.click_text(recipient_email, timeout=10, region=Search.RESULT_LIST)
        time.sleep(1)

        # 5. 验证进入聊天页面（通过加号按钮判断）
        plus_pos = self.find_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN)
        assert plus_pos is not None, "❌ 未进入聊天页面：未找到加号按钮"
        logger.info(f"📱 已进入{msg_type}聊天页面")
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
            # 10. 返回消息列表页
            self.return_to_message_list(max_back=5, strict=True)

        return message

    def send_file(self, recipient, file_name):
        is_group = recipient.isdigit()
        if is_group:
            msg_type = "群组"
        else:
            msg_type = "P2P"

        # 1. 打开搜索页面
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(0.5)

        # 2. 输入搜索关键词（SELECT_SEARCH 图片已过时，直接输入）
        self.input_text(str(recipient))
        time.sleep(1)

        # 3. 切换到对应Tab
        if is_group:
            self.click_image(os.path.join(path, "搜索页面-群tab-未选中.png"),
                             region=Search.SEARCH_TAB, dy=-10)
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
        self.click_text("共享文件夹")
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

    # styleBar 格式工具栏中每个格式按钮的 ADB 坐标
    # 通过 uiautomator dump + 实际验证确认：
    # 进入扩展编辑模式后，底部直接显示 styleBar（无需额外切换模式）
    # styleBarFl 按钮顺序：T(段落标题) / B(加粗) / I(斜体) / U(下划线) / S(删除线) / A(字色)
    # 按钮间距固定 72px，Y 中心 = 918
    _STYLE_BAR_ADB_COORDS = {
        "paragraph": (108, 918),  # btn0 [84,894][132,942]  - T (段落标题，点击弹出H1-H6)
        "bold": (180, 918),  # btn1 [156,894][204,942] - B (加粗)
        "italic": (252, 918),  # btn2 [228,894][276,942] - I (斜体)
        "underline": (324, 918),  # btn3 [300,894][348,942] - U (下划线)
        "strikethrough": (396, 918),  # btn4 [372,894][420,942] - S (删除线)
        "font_color": (459, 918),  # btn5 [444,894][474,942] - A (字色，可能需要滑动)
    }

    # flMarkdown 按钮的 ADB 坐标 — 位于 styleBar 左侧
    # 注意：新版 UI 中进入扩展编辑后直接就是 styleBar，不再需要模式切换
    _FL_MARKDOWN_ADB_COORD = (42, 918)  # [18,876][66,960] 中心

    # 需要向左滑动工具栏才能看到的格式（RecyclerView 可能需要滚动）
    _RICH_TEXT_SCROLL_FORMATS = {"font_color"}

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

    def _input_markdown_text(self, text: str) -> bool:
        """
        在 Markdown 编辑器中输入文本（处理特殊字符转义）

        Markdown 语法常含空格和特殊字符（>, `, [, ], (, ), =），
        ADB shell input text 需要将空格转义为 %s。
        对于多行文本（如代码块中的换行），逐行输入并用 Enter 键换行。

        Args:
            text: 要输入的 Markdown 语法文本

        Returns:
            bool: 输入是否成功
        """
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line:
                # 空格转义为 %s（ADB input text 要求）
                escaped = line.replace(" ", "%s")
                self._run_adb_command("shell", "input", "text", escaped)
                time.sleep(0.2)
            if i < len(lines) - 1:
                # 换行: KEYCODE_ENTER = 66
                self._run_adb_command("shell", "input", "keyevent", "66")
                time.sleep(0.2)
        logger.info(f"⌨️ Markdown 文本已输入: {text[:50]}...")
        return True

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

        # 幂等检查：如果已经在扩展编辑模式（工具栏可见），则跳过
        if self.find_image(EXTENDED_EDIT_BOLD_B, timeout=2):
            logger.info("✅ 已经在扩展编辑模式，跳过进入步骤")
            return True

        # 点击段落按钮（在输入框右侧），图片不匹配时使用 ADB 坐标(471,857)兜底
        clicked = self.find_image(CHAT_PARAGRAPH_BUTTON, region=Normal.HALF_DOWN, timeout=3)
        if clicked:
            self.click_image(CHAT_PARAGRAPH_BUTTON, region=Normal.HALF_DOWN)
        else:
            logger.warning("⚠️ 段落按钮图片未匹配，使用 ADB 坐标 (471, 857) 点击")
            self._adb_tap(471, 857)
        time.sleep(1)

        # 新版 UI 点击段落按钮后可能直接进入扩展编辑，无需再点 "Aa"
        if self.find_image(EXTENDED_EDIT_BOLD_B, timeout=2, region=Normal.HALF_DOWN):
            logger.info("✅ 已进入扩展编辑模式（直接进入，无 Aa 弹窗）")
            return True

        # 旧版 UI：弹出面板，点击 "Aa" 进入
        aa_pos = self.find_text_by_ocr("Aa", timeout=3)
        if aa_pos:
            self.tap(aa_pos[0], aa_pos[1])
        else:
            logger.warning("⚠️ 未找到 'Aa' 文字，尝试使用 ADB 坐标(471,857)再次点击段落按钮")
            self._adb_tap(471, 857)
        time.sleep(1)

        # 宽松验证：用 OCR 查看工具栏文字（B/I/U/S），比图片匹配更稳定
        in_edit = self.find_image(EXTENDED_EDIT_BOLD_B, timeout=3, region=Normal.HALF_DOWN)
        if not in_edit:
            logger.warning("⚠️ EXTENDED_EDIT_BOLD_B 图片未匹配，继续执行（样式栏可能已就绪）")

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

        # 仍在扩展编辑模式：关闭按钮(EXTENDED_EDIT_CLOSE_BUTTON)在当前版本已废弃
        # 改用左上角 "×" 文字或 ADB 坐标(27,50) 关闭，兜底按返回键
        close_pos = self.find_text_by_ocr("×", timeout=2, region=Normal.HALF_UP)
        if close_pos:
            self.tap(close_pos[0], close_pos[1])
        else:
            self._adb_tap(27, 50)
        time.sleep(0.5)
        logger.info("✅ 已关闭扩展编辑模式")

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
        # 在工具栏区域向左滑动（工具栏在底部，约 y=918）
        # Markdown 按钮在最右端，需要多次滑动才能显示
        for _ in range(3):
            self.swipe(400, 918, 100, 918, duration=0.3)
            time.sleep(0.5)
        return True

    def send_rich_text_message(self, recipient: str, message: str,
                               format_type: str) -> bool:
        """
        发送富文本格式消息

        POPO 扩展编辑模式进入后底部直接显示 styleBar 格式工具栏
        （markdownBarRecyclerView），包含 T/B/I/U/S/A 格式按钮，可直接点击。

        完整流程:
        1. 搜索联系人进入聊天页面
        2. 如果处于 Markdown 模式则退出
        3. 点击段落按钮 → Aa 进入扩展编辑模式
        4. 通过 ADB tap 点击 styleBar 中的格式按钮激活样式
        5. 输入文本
        6. 点击发送按钮
        7. 验证发送成功
        8. 退出扩展编辑模式
        9. 返回消息列表页

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

        # 2. 如果 POPO 记住了 Markdown 模式，先退出回到普通聊天输入模式
        #    Markdown 编辑器底部有 "Plain Text" 标签，按一次 back 可退出
        plain_pos = self.find_text_by_ocr("Plain", timeout=2)
        if plain_pos:
            logger.info("⚠️ 检测到 Markdown 编辑器模式，退出回到普通输入模式")
            self.press_back()
            time.sleep(1)
            # 验证回到了普通聊天页面（有"发送给"文字），如果没有则再按一次
            if not self.find_text_by_ocr("发送给", timeout=3):
                # 可能已退出聊天页面，需重新进入
                self._enter_chat_page(recipient)

        # 3. 进入扩展编辑模式（直接显示 styleBar 格式工具栏）
        self._enter_extended_edit_mode()

        # 4. 通过 ADB tap 点击格式按钮激活样式（滑动如需要）
        self._scroll_toolbar_to_format(format_type)
        ax, ay = adb_coord
        logger.info(f"📝 通过 ADB 点击格式按钮 '{format_type}' @ ({ax}, {ay})")
        self._adb_tap(ax, ay)
        time.sleep(0.5)

        # 5. 输入文本（扩展编辑模式中输入区域已聚焦，直接输入即可）
        self.input_text(str(message))
        time.sleep(0.5)

        # 6. 点击发送按钮
        self.click_image(EXTENDED_EDIT_SEND_BUTTON, region=Normal.HALF_DOWN)
        time.sleep(1)

        # 7. 验证发送成功：消息文本出现在聊天区域
        self.text_exists(message, timeout=5)

        # 8. 退出扩展编辑模式
        self._exit_extended_edit_mode()
        time.sleep(0.5)

        # 9. 返回消息列表页
        self.return_to_message_list(max_back=5)

        logger.info(f"✅ [MuMu] 富文本消息发送成功: format={format_type}")
        return True

    # Markdown 语法类型映射：markdown_type -> (语法模板函数, 日志描述)
    # 语法模板函数接收 text 和可选参数，返回 (markdown_text, verify_text)
    _MARKDOWN_SYNTAX_MAP = {
        "hyperlink": lambda text, url="https://www.163.com", **kw: (f"[{text}]({url})", text),
        "quote": lambda text, **kw: (f"> {text}", text),
        "inline_code": lambda text, **kw: (f"`{text}`", text),
        "code_block": lambda text, language="", **kw: (f"```{language}\n{text}\n```", text.split('\n')[0]),
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

        # 2-3. 进入 Markdown 编辑器
        # 检查是否已经在 Markdown 编辑模式（POPO 会记住上次的编辑状态）
        plain_pos = self.find_text_by_ocr("Plain", timeout=2)
        if plain_pos:
            logger.info("📝 已在 Markdown 编辑模式（POPO 记住了状态），跳过进入步骤")
        else:
            # 需要进入扩展编辑模式；新版 UI 已无独立 Markdown 按钮
            # 直接在扩展编辑输入区域输入 Markdown 语法
            self._enter_extended_edit_mode()
            time.sleep(0.5)

        # 4. 在 Markdown 编辑器中输入文本
        #    Markdown 编辑器进入后焦点默认在编辑区域，直接输入即可
        #    如果焦点不在，先点击 "Plain" 标签下方 dy=40 定位到编辑区域
        self._input_markdown_text(markdown_text)
        time.sleep(0.5)

        # 5. 检查文本是否输入成功；聚焦方式改用坐标，不依赖"Plain"文字
        verify_word = markdown_text.replace(">", "").replace("`", "").replace("=", "").replace("[", "").replace("]", "").strip()[:5]
        if verify_word and not self.find_text_by_ocr(verify_word, timeout=2):
            logger.info("⚠️ 首次输入未成功，点击输入区域(270,180)后重试")
            self.tap(270, 180)  # 扩展编辑模式输入框在顶部 y≈165-200
            time.sleep(0.3)
            self._input_markdown_text(markdown_text)
            time.sleep(0.5)

        # 6. 发送（发送按钮在底部工具栏右侧）
        send_pos = self.find_image(EXTENDED_EDIT_SEND_BUTTON, timeout=3)
        if send_pos:
            self.click_image(EXTENDED_EDIT_SEND_BUTTON, region=Normal.HALF_DOWN)
        else:
            # 发送按钮可能被键盘遮挡，用 ADB 直接点击已知坐标
            logger.info("⚠️ 发送按钮不可见，通过 ADB 直接点击")
            self._adb_tap(505, 922)
        time.sleep(1)

        # 7. 验证发送成功：检查已回到正常聊天输入模式（扩展编辑器已关闭）
        if not self.find_text_by_ocr("发送给", timeout=5):
            # 发送后编辑器未自动关闭，手动退出再检查
            self._exit_extended_edit_mode()
        assert self.find_text_by_ocr("发送给", timeout=5) is not None, \
            f"发送后未回到正常聊天模式，'{markdown_type}' 消息发送可能失败"

        # 8. 退出扩展编辑模式
        self._exit_extended_edit_mode()
        time.sleep(0.5)

        # 9. 返回消息列表页
        self.return_to_message_list(max_back=5)

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
        # SIDEBAR_MY_COLLECTION 用作视觉锚点定位，用户名在其上方约180px
        # image/ 版匹配 score=0.557, image_ai/ 版=0.263，使用 image/ 版
        import os
        my_coll = os.path.join(r'E:\UIAutotest\image', '侧边栏-我的收藏.png')
        self.click_image(my_coll, dx=0, dy=-180, threshold=0.55, timeout=10)
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

        # 验证进入聊天页：底部出现"发送给"（普通模式）或"Plain"（扩展编辑模式被记忆）
        pos = self.find_text_by_ocr("发送给", timeout=3)
        if pos is None:
            # POPO可能记住了上次的扩展编辑模式，输入区域显示"Plain Text"
            # OCR可能识别为"PlainText"或"Plain Text"，用"Plain"做子串匹配
            pos = self.find_text_by_ocr("Plain", timeout=2)
            assert pos is not None, "进入聊天页失败: 底部未找到'发送给'或'Plain Text'"
        logger.info(f"[MuMu] 已进入聊天页: {recipient}")

    def send_image(self):
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

        self.send_image()

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

        # 以 CHAT_PLUS_BUTTON 为锚点定位已发送图片气泡（图片在+号上方约250px，右对齐）
        plus_pos = self.find_image(CHAT_PLUS_BUTTON, region=Normal.HALF_DOWN, timeout=10)
        if plus_pos:
            img_x, img_y = 370, plus_pos[1] - 250
        else:
            # 如果找不到+号，直接用 CHAT_SENT_IMAGE_BUBBLE 图片匹配兜底
            logger.warning("⚠️ 未找到+按钮，尝试图片匹配 CHAT_SENT_IMAGE_BUBBLE")
            img_pos = self.find_image(CHAT_SENT_IMAGE_BUBBLE, timeout=10)
            assert img_pos is not None, "未找到已发送图片气泡"
            img_x, img_y = img_pos

        self.long_press(img_x, img_y, duration=1.5)
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
        # IMAGE_EDITOR_H 图片模板已过时，改用短暂等待代替断言
        time.sleep(0.5)
        logger.info("✏️ H 图案绘制完成")
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
        """搜索"""

        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)

        # tab左滑翻页（云空间/应用 在 tab 行右侧，需先左滑露出）
        if tab in ["云空间", "应用"]:
            # 先左滑让隐藏的 tab 出现，再用图片点击，不依赖 text_exists
            self.swipe(420, 133, 80, 133, duration=0.4)
            time.sleep(0.5)
        img_name = f"搜索页面-{tab}tab.png"
        img_name_miss = f"搜索页面-{tab}tab-未选中.png"
        if tab == "全部":
            pass
        else:
            logger.info(f"tab是：{tab}")
            self.click_image(os.path.join(path, img_name_miss), dy=-10, region=Search.SEARCH_TAB, y=133)
        self.image_exists(img_name, region=Search.SEARCH_TAB)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(text))
        if isclose:
            # 点击取消按钮，退出搜索页面
            self.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    # ==================== 群组管理相关 ====================

    def _enter_group_settings_legacy(self, group_identifier: str) -> None:
        """已废弃，保留供旧调用兼容，实际由下方 _enter_group_settings(bool) 覆盖"""
        return self._enter_group_settings(group_identifier)

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
        self.return_to_message_list(max_back=8)

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
        self.return_to_message_list(max_back=8)

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
        time.sleep(0.5)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(str(group_identifier))
        time.sleep(1)
        self.click_text("群", region=Normal.HALF_UP)
        time.sleep(2)

        # 2. 点击第一个群搜索结果（群名行，避开顶部筛选按钮区域）
        # 群 tab 下布局: 筛选按钮 y≈178, 第一个群名 y≈240, 包含副文本 y≈278
        pos = self.find_text_by_ocr("包含", timeout=10)
        if pos:
            # "包含" 副文本在群名下方约 35px，点击其上方进入群聊
            self.tap(270, pos[1] - 35)
        else:
            # 没有"包含"文字时，直接点击第一个结果区域
            self.tap(270, 252)
        time.sleep(2)

        # 3. 验证已进入群聊天页（检查"名群成员"文字）
        members_pos = self.find_text_by_ocr("名群成员", timeout=5)
        if not members_pos:
            logger.warning("⚠️ 未检测到'名群成员'，尝试直接点击标题栏进入群设置")
            self.tap(265, 70)
            time.sleep(2)
        else:
            # 4. 点击群名称区域进入群设置
            self.tap(265, 70)
            time.sleep(2)

        # 5. 验证进入群设置页面
        if self.find_text_by_ocr("设置", timeout=5):
            logger.info("✅ [MuMu] 已进入群设置页面")
            return True

        # 备选验证：检查群设置页特征元素
        if self.find_text_by_ocr("群公告", timeout=3) or self.find_text_by_ocr("群成员", timeout=3):
            logger.info("✅ [MuMu] 已进入群设置页面（通过特征元素确认）")
            return True

        logger.error("❌ [MuMu] 进入群设置失败")
        return False

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
        self.return_to_message_list()

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
        self.return_to_message_list()

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
        self.click_image(ALL_TAB_PLUS, region=Normal.HALF_UP)
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
        self.click_image(ADDLINK_OK_BUTTON, region=Normal.HALF_UP)
        time.sleep(2)

        # 9. 验证标签页添加成功（应该在标签页列表中看到新标签页）
        self.find_text_by_ocr(tab_name, timeout=5)
        logger.info(f"✅ [MuMu] 标签页 '{tab_name}' 添加成功")

        # 10. 返回消息列表页
        self.return_to_message_list()

        logger.info("✅ [MuMu] 添加自定义标签页完成")
        return True

    def remove_custom_tab_page(self, recipient: str, tab_name: str) -> bool:
        """
        P2P会话删除自定义标签页（清理用）

        管理标签页屏幕 UI 说明：
        - 左侧红/蓝 icon：切换展示/隐藏，不是删除
        - 右侧三点按钮（x≈510）：点击后底部弹出 BottomSheet，可执行删除

        步骤:
        1. 进入P2P设置→标签页管理
        2. 点击"+"展开管理面板
        3. 点击"管理"
        4. 找到目标标签页，点击右侧三点按钮
        5. 在底部弹窗中点击删除
        6. 返回消息列表页

        Args:
            recipient: 联系人标识
            tab_name: 要删除的标签页名称

        Returns:
            bool: True=找到并尝试删除，False=标签页不存在
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

        # 5. 找到目标标签页
        tab_pos = self.find_text_by_ocr(tab_name, timeout=5)
        if not tab_pos:
            # 标签页不存在，退出管理页面
            self.return_to_message_list()
            logger.info(f"ℹ️ [MuMu] 标签页 '{tab_name}' 不存在，无需删除")
            return False

        # 6. 点击该行右侧的三点更多按钮（x≈510，屏幕最右侧）
        self.tap(510, tab_pos[1])
        time.sleep(1.5)

        # 7. 在底部弹窗中点击删除（兼容"删除"/"移除"两种文案）
        deleted = False
        for confirm_text in ["删除", "移除"]:
            if self.find_text_by_ocr(confirm_text, timeout=3):
                self.click_text(confirm_text, timeout=3)
                time.sleep(1)
                deleted = True
                break

        if not deleted:
            logger.warning(f"⚠️ [MuMu] 未在弹窗中找到删除选项，标签页 '{tab_name}' 可能未成功删除")

        # 8. 返回消息列表页
        self.return_to_message_list()

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

        # 6. 验证已发送（兼容不同版本文案，toast 出现速度快，宽松处理）
        sent_ok = self.find_text_by_ocr("已发送", timeout=4)
        if not sent_ok:
            sent_ok = self.find_text_by_ocr("发送成功", timeout=2)
        if not sent_ok:
            logger.warning("⚠️ 未检测到'已发送'/'发送成功' toast，继续验证聊天记录卡片")

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

        # 5. 验证"复制成功"（兼容不同版本文案）
        ok = self.find_text_by_ocr("复制成功", timeout=3)
        if not ok:
            ok = self.find_text_by_ocr("已复制", timeout=2)
        if not ok:
            logger.warning("⚠️ 未检测到'复制成功'或'已复制' toast，继续执行")
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
        self.return_to_message_list(max_back=5)

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
        logger.info("📸 3张图片发送成功")

        # 3. 以+按钮为锚点定位图片气泡（全屏搜索，超时10s）
        plus_pos = self.find_image(CHAT_PLUS_BUTTON, timeout=10)
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

        # 9. 验证已发送（兼容不同版本文案）
        sent_ok = self.find_text_by_ocr("已发送", timeout=4)
        if not sent_ok:
            sent_ok = self.find_text_by_ocr("发送成功", timeout=2)
        if not sent_ok:
            logger.warning("⚠️ 未检测到'已发送'/'发送成功' toast，继续验证聊天记录")

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
        self.return_to_message_list()

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
        self.return_to_message_list(max_back=5)

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
        self.return_to_message_list()

        logger.info("✅ [MuMu] 应用外分享图片到POPO成功")
        return True

    # ==================== 群设置页功能 ====================

    def _enter_group_chat_from_list(self, group_name_keyword: str) -> None:
        """
        从会话列表直接点击群聊进入群聊天页面

        在消息列表页 OCR 扫描找到含有指定关键词的群会话，直接点击进入。
        适用于群名在会话列表可见的场景。

        Args:
            group_name_keyword: 群名关键词（如"内购"/"吴彦祖"）

        Raises:
            AssertionError: 会话列表中找不到匹配的群
        """
        logger.info(f"🔍 [MuMu] 从会话列表进入群聊: {group_name_keyword}")

        # 先确保在消息列表页（防止残留在群设置/聊天等页面）
        self._ensure_message_page()
        time.sleep(1)

        # 先滚动回列表顶部（防止之前滑动导致目标群不可见）
        for _ in range(3):
            self.swipe_down(400)
            time.sleep(0.3)

        # 在消息列表中查找含关键词的会话（最多滑动3次）
        for scroll in range(4):
            results = self.ocr_scan_page()
            for r in results:
                text = r.get('text', '')
                cy = r.get('cy', 0)
                cx = r.get('cx', 0)
                if group_name_keyword in text and 280 < cy < 850:
                    logger.info(f"✅ 找到群会话: '{text}' at ({cx},{cy})")
                    self.tap(270, cy)
                    time.sleep(2)
                    return
            if scroll < 3:
                self.swipe_up(300)
                time.sleep(0.5)

        assert False, f"会话列表中未找到含 '{group_name_keyword}' 的群聊"

    def _enter_group_settings_from_chat(self) -> None:
        """
        从群聊天页面进入群设置页面

        点击群聊页面顶部群名称区域进入群设置。

        前置条件: 当前在群聊天页面
        """
        logger.info("⚙️ [MuMu] 从群聊进入群设置")

        # 群聊页面顶部有"N名群成员"文字，点击其上方进入群设置
        members_pos = self.find_text_by_ocr("名群成员", timeout=5)
        if members_pos:
            self.tap(members_pos[0], members_pos[1], dy=-30)
        else:
            # 备选：直接点击标题栏中部
            self.tap(270, 55)
        time.sleep(2)

        logger.info("✅ [MuMu] 已进入群设置页面")

    def return_to_message_list(self, max_back: int = 6, strict: bool = False) -> None:
        """
        从任意页面返回到消息列表页

        Args:
            max_back: 最大返回次数，默认6
            strict:   True 时若未能回到消息列表页则 assert 失败
        """
        for i in range(max_back):
            self.press_back()
            time.sleep(0.5)
            if self.find_image(MESSAGE_TAB_BLUE, timeout=1):
                logger.info("✅ 已返回消息列表页")
                return
        if strict:
            assert False, f"❌ 返回消息列表页失败：连续 {max_back} 次未找到 MESSAGE_TAB_BLUE"
        logger.warning("⚠️ 可能未完全返回消息列表页")

    def open_group_settings_page(self, group_name_keyword: str) -> bool:
        """
        从会话列表进入群设置页面

        步骤:
        1. 在消息列表中找到群聊并点击进入
        2. 点击群名称进入群设置
        3. 验证到达群设置页面

        Args:
            group_name_keyword: 群名关键词

        Returns:
            bool: 是否成功进入群设置页面
        """
        logger.info(f"⚙️ [MuMu] 进入群设置页面: {group_name_keyword}")

        self._enter_group_settings(group_name_keyword)

        # 验证到达群设置页面
        pos = self.find_text_by_ocr("群公告", timeout=10)
        if pos is None:
            self.swipe_up(200)
            time.sleep(0.5)
            pos = self.find_text_by_ocr("群公告", timeout=5)
        assert pos is not None, "未进入群设置页面：找不到'群公告'"

        logger.info("✅ [MuMu] 已进入群设置页面")
        return True

    def check_group_message_reminder(self, group_name_keyword: str) -> bool:
        """
        检查群消息提醒开关并切换

        步骤:
        1. 进入群设置页面
        2. 找到"消息提醒"开关
        3. 点击切换
        4. 返回消息列表页

        Args:
            group_name_keyword: 群名关键词

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔔 [MuMu] 切换群消息提醒: {group_name_keyword}")

        self._enter_group_settings(group_name_keyword)

        # 在群设置页中查找"消息提醒"
        for scroll in range(3):
            pos = self.find_text_by_ocr("消息提醒", timeout=3)
            if pos is not None:
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert pos is not None, "群设置页面中未找到'消息提醒'"
        logger.info(f"✅ 找到消息提醒选项 at {pos}")

        # 点击开关（开关在文字右侧）
        self.click_text("消息提醒", dx=200, timeout=5)
        time.sleep(1)

        self.return_to_message_list()
        logger.info("✅ [MuMu] 群消息提醒切换完成")
        return True

    def verify_group_setting_default(self, group_name_keyword: str, setting_name: str) -> str:
        """
        验证群设置页面中某个设置项是否存在

        步骤:
        1. 进入群设置页面
        2. 逐屏查找指定设置项
        3. 截图记录状态
        4. 返回

        Args:
            group_name_keyword: 群名关键词
            setting_name: 设置项名称

        Returns:
            str: "found" 表示找到
        """
        logger.info(f"🔍 [MuMu] 验证群设置: {setting_name}")

        self._enter_group_settings(group_name_keyword)

        found = False
        for screen in range(5):
            pos = self.find_text_by_ocr(setting_name, timeout=3)
            if pos is not None:
                found = True
                logger.info(f"✅ 在第{screen + 1}屏找到 '{setting_name}' at {pos}")
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert found, f"群设置页面中未找到 '{setting_name}'"

        self.take_screenshot(
            save_path=f'E:\\UIAutotest\\explorer_output\\screenshots\\group_setting_{setting_name}.png'
        )

        self.return_to_message_list()
        logger.info(f"✅ [MuMu] 群设置 '{setting_name}' 验证完成")
        return "found"

    def check_group_settings_item(self, group_identifier: str, item_name: str) -> dict:
        """
        在群设置页查找指定设置项

        步骤:
        1. 进入群设置页面
        2. OCR 查找指定项目名称
        3. 若未找到，向上滑动继续查找
        4. 返回消息列表页

        Args:
            group_identifier: 群组标识（群号或群名关键词）
            item_name: 设置项名称（如"消息提醒"/"自动翻译"/"入群验证"/"群管理"）

        Returns:
            dict: 包含 found/position/screen_index/item_name
        """
        logger.info(f"🔍 [MuMu] 查找群设置项: {item_name}")

        self._enter_group_settings(group_identifier)

        found = False
        position = None
        screen_index = None
        for screen in range(5):
            position = self.find_text_by_ocr(item_name, timeout=2, region=Normal.HALF_UP)
            if not position:
                position = self.find_text_by_ocr(item_name, timeout=2, region=Normal.HALF_DOWN)
            if position:
                found = True
                screen_index = screen
                logger.info(f"✅ 找到设置项 '{item_name}' @ {position} (第{screen + 1}屏)")
                break
            self.swipe_up(300)
            time.sleep(0.5)

        self.return_to_message_list()

        return {
            "found": found,
            "position": position,
            "screen_index": screen_index,
            "item_name": item_name,
        }

    def open_group_qr_code(self, group_identifier: str) -> bool:
        """
        打开群二维码页面

        步骤:
        1. 进入群设置页面
        2. 点击群二维码入口
        3. 验证二维码页面出现
        4. 返回

        Args:
            group_identifier: 群组标识（群号或群名关键词）

        Returns:
            bool: 是否成功打开
        """
        logger.info(f"📱 [MuMu] 打开群二维码: {group_identifier}")

        self._enter_group_settings(group_identifier)

        # 群二维码入口在群设置第一屏 - 点击群名称右侧二维码icon
        clicked = False
        for title in [group_identifier, "群聊名称", "群名称"]:
            try:
                self.click_text(title, dx=200, timeout=3, region=Normal.HALF_UP)
                clicked = True
                break
            except AssertionError:
                continue
        assert clicked, "未找到群二维码入口"
        time.sleep(1.5)

        # 验证二维码页面
        self.find_text_by_ocr("有效", timeout=5, region=Normal.HALF_UP)

        logger.info("✅ [MuMu] 已打开群二维码页面")
        # 返回群设置页面
        self.press_back()
        time.sleep(1)
        self.text_exists("群公告", timeout=5)
        return True

    def open_group_announcement(self, group_identifier: str) -> bool:
        """
        打开群公告页面

        步骤:
        1. 进入群设置页面
        2. 点击"群公告"
        3. 验证进入公告页面

        Args:
            group_identifier: 群组标识（群号或群名关键词）

        Returns:
            bool: 是否成功进入
        """
        logger.info(f"📢 [MuMu] 打开群公告页面: {group_identifier}")

        self._enter_group_settings(group_identifier)

        self.click_text("群公告", timeout=5, region=Normal.HALF_DOWN)
        time.sleep(1.5)

        if self.find_image(GROUP_ANNOUNCEMENT_EMPTY_PLACEHOLDER, timeout=2):
            logger.info("✅ 群公告页为空占位符已出现")
        else:
            self.find_text_by_ocr("编辑", timeout=3)

        logger.info("✅ [MuMu] 已进入群公告页面")
        return True

    def open_group_announcement_page(self, group_name_keyword: str) -> bool:
        """
        打开群公告页面

        步骤:
        1. 进入群设置页面
        2. 点击"群公告"
        3. 验证进入公告页面
        4. 返回

        Args:
            group_name_keyword: 群名关键词

        Returns:
            bool: 是否成功进入
        """
        logger.info(f"📢 [MuMu] 打开群公告页面: {group_name_keyword}")

        self._enter_group_settings(group_name_keyword)

        # 点击"群公告"
        self.click_text("群公告", timeout=5)
        time.sleep(1.5)

        self.take_screenshot(
            save_path=r'E:\UIAutotest\explorer_output\screenshots\group_announcement_page.png'
        )

        logger.info("✅ [MuMu] 已打开群公告页面")
        self.return_to_message_list()
        return True

    # ==================== 群设置扩展方法 (用于28个单设备用例) ====================

    def click_in_group_settings(self, group_identifier: str, click_text: str,
                                verify_text: str = None, region=None) -> bool:
        """
        进入群设置后点击指定文字项，并可选验证新页面

        步骤:
        1. 进入群设置页面
        2. 逐屏滑动查找 click_text
        3. 点击该文字
        4. 若提供 verify_text，验证新页面包含该文字
        5. 返回消息列表页

        Args:
            group_identifier: 群关键词
            click_text: 要点击的文字
            verify_text: 点击后新页面应包含的文字（可选）
            region: 点击区域限定

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"👆 [MuMu] 群设置中点击 '{click_text}' (验证: {verify_text})")

        self._enter_group_settings(group_identifier)

        # 逐屏查找并点击
        clicked = False
        for screen in range(5):
            pos = self.find_text_by_ocr(click_text, timeout=2, region=region)
            if pos:
                self.tap(pos[0], pos[1])
                clicked = True
                logger.info(f"✅ 已点击 '{click_text}'")
                time.sleep(1.5)
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert clicked, f"群设置页面未找到 '{click_text}'"

        # 验证新页面
        if verify_text:
            found = self.find_text_by_ocr(verify_text, timeout=5)
            assert found, f"点击 '{click_text}' 后未找到 '{verify_text}'"
            logger.info(f"✅ 新页面包含 '{verify_text}'")

        # 返回
        self.return_to_message_list()
        return True

    def toggle_group_setting_switch(self, group_identifier: str, setting_name: str,
                                    dx: int = 200) -> bool:
        """
        切换群设置页中某开关

        步骤:
        1. 进入群设置页
        2. 查找 setting_name 文字位置
        3. 点击文字右侧 +dx 像素处切换开关
        4. 返回消息列表页

        Args:
            group_identifier: 群关键词
            setting_name: 开关对应的文字标签
            dx: 开关相对文字的x偏移（默认+200，开关在右侧）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔀 [MuMu] 切换群设置开关 '{setting_name}'")

        self._enter_group_settings(group_identifier)

        # 查找开关对应的文字
        found_pos = None
        for screen in range(5):
            pos = self.find_text_by_ocr(setting_name, timeout=2)
            if pos:
                found_pos = pos
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert found_pos, f"群设置页面未找到 '{setting_name}'"
        # 点击开关（右侧）
        self.tap(found_pos[0] + dx, found_pos[1])
        time.sleep(1)
        logger.info(f"✅ 开关已切换")

        self.return_to_message_list()
        return True

    def edit_group_description(self, group_identifier: str, description: str) -> bool:
        """
        编辑群描述

        步骤:
        1. 进入群设置页面
        2. 点击 "群描述"
        3. 在编辑页输入新描述
        4. 点击保存
        5. 验证toast "群描述修改成功" 或返回到设置页
        6. 返回消息列表页

        Args:
            group_identifier: 群关键词
            description: 新群描述内容

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📝 [MuMu] 编辑群描述: {description[:30]}")

        self._enter_group_settings(group_identifier)

        # 滑动查找群描述
        pos = None
        for screen in range(3):
            pos = self.find_text_by_ocr("群描述", timeout=2)
            if pos:
                break
            self.swipe_up(300)
            time.sleep(0.5)
        assert pos, "未找到群描述入口"

        self.tap(pos[0], pos[1])
        time.sleep(1.5)

        # 进入编辑页后清空并输入
        self.clear_input()
        time.sleep(0.3)
        self.input_text(description)
        time.sleep(0.5)

        # 点击保存/完成按钮
        self.press_back()  # 收起键盘
        time.sleep(0.5)
        saved = False
        for btn in ["保存", "完成"]:
            try:
                self.click_text(btn, timeout=2, region=Normal.HALF_UP)
                saved = True
                break
            except AssertionError:
                continue
        if not saved:
            # 点击右上角确认按钮
            self._adb_tap(486, 107)
        time.sleep(1.5)

        logger.info(f"✅ 群描述已编辑")
        self.return_to_message_list()
        return True

    def open_group_member_list(self, group_identifier: str) -> bool:
        """
        打开群成员列表

        步骤:
        1. 进入群设置页面
        2. 点击 "群成员" 或 "N人"
        3. 验证进入群成员列表页

        Args:
            group_identifier: 群关键词

        Returns:
            bool: 是否成功打开
        """
        logger.info(f"👥 [MuMu] 打开群成员列表: {group_identifier}")

        self._enter_group_settings(group_identifier)

        # 点击 "群成员"
        self.click_text("群成员", timeout=5, region=Normal.HALF_UP)
        time.sleep(1.5)

        logger.info("✅ 已打开群成员列表")
        return True

    def click_group_qr_code(self, group_identifier: str) -> bool:
        """
        打开群二维码页面（不关闭，用于后续操作）

        Args:
            group_identifier: 群关键词

        Returns:
            bool: 是否成功打开
        """
        logger.info(f"📱 [MuMu] 打开群二维码页面: {group_identifier}")
        self._enter_group_settings(group_identifier)

        # 群二维码入口在群设置第一屏 - 群名称右侧icon
        clicked = False
        for title in [group_identifier, "群聊名称", "群名称"]:
            try:
                self.click_text(title, dx=200, timeout=3, region=Normal.HALF_UP)
                clicked = True
                break
            except AssertionError:
                continue
        assert clicked, "未找到群二维码入口"
        time.sleep(1.5)

        # 验证进入二维码页
        self.find_text_by_ocr("有效", timeout=5, region=Normal.HALF_UP)
        logger.info("✅ 已打开群二维码页面")
        return True

    # ==================== 群主测试群管理 ====================

    def _find_group_in_session_list(self, keyword: str, max_scrolls: int = 5) -> bool:
        """
        通过搜索功能查找是否存在含指定关键词的群组

        Args:
            keyword: 群名关键词
            max_scrolls: 未使用，保留兼容

        Returns:
            bool: 是否找到
        """
        self._ensure_message_page()
        time.sleep(0.5)

        # 点击搜索
        self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
        time.sleep(0.5)
        self.click_image(SELECT_SEARCH, dx=10)
        self.input_text(keyword)
        time.sleep(1)

        # 切换到"群"Tab
        try:
            self.click_image(SEARCH_TAB3_NO, timeout=3, region=Normal.HALF_UP)
            # self.click_text("群", timeout=3, region=Normal.HALF_UP)
            time.sleep(1)
        except AssertionError:
            pass

        # 检查是否有搜索结果
        no_result = self.find_text_by_ocr("没有找到", timeout=2)
        if no_result:
            # 退出搜索
            self.click_text("取消", timeout=2, region=Normal.HALF_UP)
            time.sleep(0.5)
            return False

        # 有结果，退出搜索
        self.click_text("取消", timeout=2, region=Normal.HALF_UP)
        time.sleep(0.5)
        return True

    def rename_group_name(self, current_group_keyword: str, new_name: str) -> bool:
        """
        群主修改群名

        步骤:
        1. 进入群设置
        2. 点击"群名称"
        3. 清空并输入新名字
        4. 点击保存/完成按钮
        5. 返回消息列表页

        Args:
            current_group_keyword: 当前群名/群号关键词
            new_name: 新群名

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"✏️ [MuMu] 修改群名: {current_group_keyword} → {new_name}")

        self._enter_group_settings(current_group_keyword)

        # 点击"群名称"
        found = False
        for screen in range(3):
            pos = self.find_text_by_ocr("群名称", timeout=2)
            if pos:
                self.tap(pos[0], pos[1])
                found = True
                time.sleep(1.5)
                break
            self.swipe_up(300)
            time.sleep(0.5)
        assert found, "未找到群名称入口"

        # 清空 + 输入新名字
        self.clear_input()
        time.sleep(0.3)
        self.input_text(new_name)
        time.sleep(0.5)

        # 点击保存
        self.press_back()  # 收起键盘
        time.sleep(0.5)
        saved = False
        for btn in ["保存", "完成", "确定"]:
            try:
                self.click_text(btn, timeout=2, region=Normal.HALF_UP)
                saved = True
                break
            except AssertionError:
                continue
        if not saved:
            self._adb_tap(486, 107)  # 右上角确认
        time.sleep(2)

        logger.info(f"✅ [MuMu] 群名已修改: {new_name}")
        # 返回消息列表
        self.return_to_message_list()
        return True

    def setup_owner_group(self, desired_name: str = "自动化测试群主群") -> str:
        """
        确保当前账号有一个作为群主的固定名测试群。
        如果已存在则直接返回群名；否则通过 create_team 创建新群并改名。

        步骤:
        1. 在会话列表查找 desired_name
        2. 找到 → 直接返回
        3. 未找到 → 调用 create_team 创建新群
        4. 新群默认名由成员组合，立即改名为 desired_name
        5. 返回 desired_name

        Args:
            desired_name: 期望的群名

        Returns:
            str: 群名，用作后续测试的 group_identifier
        """
        logger.info(f"🎯 [MuMu] setup_owner_group: {desired_name}")

        # Step 1: 检查是否已有
        if self._find_group_in_session_list(desired_name):
            logger.info(f"✅ 已存在群主测试群 '{desired_name}'，直接复用")
            return desired_name

        logger.info(f"⚠️ 未找到 '{desired_name}'，开始创建新群...")

        # Step 2: 创建新群
        self._ensure_message_page()
        time.sleep(1)
        try:
            self.create_team()
            time.sleep(2)
        except Exception as e:
            logger.error(f"❌ create_team 失败: {e}")
            raise

        # 创建成功后应该在新群的聊天页。获取群名 (顶部标题)
        # 通过OCR 顶部区域拿到默认群名
        time.sleep(2)
        results = self.ocr_scan_page()
        default_group_name = None
        for r in results:
            cy = r.get('cy', 0)
            cx = r.get('cx', 0)
            t = r.get('text', '')
            # 顶部标题区 y<100, 中部
            if 40 < cy < 100 and 150 < cx < 400 and len(t) > 2:
                default_group_name = t
                break

        logger.info(f"新创建群默认名: {default_group_name}")

        # Step 3: 进入群设置改群名
        # 当前在聊天页，直接点击群名进入群设置
        # members_pos = self.find_text_by_ocr("名群成员", timeout=5)
        members_pos = self.find_image(MSG_team_CALL, timeout=5)
        if not members_pos:
            # 兼容其他文字：N人
            logger.warning("未找到'名群成员'，尝试点击标题栏中部")
            self.tap(270, 55)
        else:
            self.tap(members_pos[0], members_pos[1], dx=-150)
        time.sleep(2)

        # 在群设置页改群名
        pos = self.find_text_by_ocr("设置", timeout=2)
        assert pos, "群设置页未找到'群名称'"
        self.tap(pos[0], pos[1], dy=120)
        self.text_exists("群信息", timeout=2)
        self.click_image(GROUP_INFO_EDITING_BUTTON, timeout=2, region=Normal.HALF_UP)
        time.sleep(1.5)

        self.clear_input()
        time.sleep(0.3)
        self.input_text(desired_name)
        time.sleep(0.3)
        self.click_image(ADDLINK_OK_BUTTON, timeout=3)

        self.press_back()
        time.sleep(0.3)
        # saved = False
        # if self.click_text("群名称修改成功", timeout=2, region=Normal.HALF_UP):
        #     saved = True
        # if not saved:
        #     self._adb_tap(486, 107)
        # time.sleep(0.5)

        # 返回消息列表
        self.return_to_message_list(max_back=4)

        logger.info(f"✅ [MuMu] 已创建并改名为 '{desired_name}'")
        return desired_name

    # ==================== 群管理子页面操作 ====================

    def enter_group_management(self, group_identifier: str) -> bool:
        """
        进入群管理子页面 (群主专属入口)

        步骤:
        1. 进入群设置
        2. 找到并点击"群管理"
        3. 验证进入群管理页

        Args:
            group_identifier: 群关键词

        Returns:
            bool: 是否成功进入
        """
        logger.info(f"🔧 [MuMu] 进入群管理: {group_identifier}")
        self._enter_group_settings(group_identifier)
        time.sleep(1)

        # 滑动查找"群管理"
        pos = None
        for screen in range(5):
            pos = self.find_text_by_ocr("群管理", timeout=2)
            if pos:
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert pos, "未找到'群管理'入口（当前账号可能不是群主）"
        self.tap(pos[0], pos[1])
        time.sleep(2)

        logger.info("✅ 已进入群管理页")
        return True

    def verify_in_group_management(self, group_identifier: str, setting_name: str) -> str:
        """
        进入群管理子页面，查找指定设置项

        步骤:
        1. 进入群设置
        2. 点击群管理
        3. 在群管理页逐屏查找 setting_name
        4. 返回消息列表

        Args:
            group_identifier: 群关键词
            setting_name: 设置项名称（如"转让群主"/"群管理员"/"解散群组"）

        Returns:
            str: "found" 表示找到
        """
        logger.info(f"🔍 [MuMu] 在群管理中查找 '{setting_name}'")
        self.enter_group_management(group_identifier)

        found = False
        for screen in range(5):
            pos = self.find_text_by_ocr(setting_name, timeout=2)
            if pos:
                found = True
                logger.info(f"✅ 找到 '{setting_name}' at {pos} (第{screen + 1}屏)")
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert found, f"群管理页面中未找到 '{setting_name}'"

        # 返回消息列表
        self.return_to_message_list()

        logger.info(f"✅ 验证 '{setting_name}' 完成")
        return "found"

    def click_in_group_management(self, group_identifier: str, click_text: str,
                                  verify_text: str = None) -> bool:
        """
        进入群管理页后点击指定项，验证新页面

        Args:
            group_identifier: 群关键词
            click_text: 要点击的文字
            verify_text: 点击后新页面应包含的文字（可选）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"👆 [MuMu] 群管理中点击 '{click_text}' (验证: {verify_text})")
        self.enter_group_management(group_identifier)

        # 滑动查找并点击
        clicked = False
        for screen in range(5):
            pos = self.find_text_by_ocr(click_text, timeout=2)
            if pos:
                self.tap(pos[0], pos[1])
                clicked = True
                time.sleep(1.5)
                break
            self.swipe_up(300)
            time.sleep(0.5)
        assert clicked, f"群管理页未找到 '{click_text}'"

        # 验证新页面
        if verify_text:
            found = self.find_text_by_ocr(verify_text, timeout=5)
            assert found, f"点击 '{click_text}' 后未找到 '{verify_text}'"

        # 返回消息列表
        self.return_to_message_list()
        return True

    def toggle_group_management_switch(self, group_identifier: str, setting_name: str,
                                       dx: int = 200) -> bool:
        """
        在群管理页切换开关

        Args:
            group_identifier: 群关键词
            setting_name: 开关名称
            dx: 开关相对文字的x偏移

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"🔀 [MuMu] 群管理切换开关 '{setting_name}'")
        self.enter_group_management(group_identifier)

        found_pos = None
        for screen in range(5):
            pos = self.find_text_by_ocr(setting_name, timeout=2)
            if pos:
                found_pos = pos
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert found_pos, f"群管理页未找到 '{setting_name}'"
        self.tap(found_pos[0] + dx, found_pos[1])
        time.sleep(1)

        # 返回消息列表
        self.return_to_message_list()
        logger.info(f"✅ 开关已切换")
        return True

    # ==================== 通讯录群组批量管理 ====================

    def open_contacts_groups(self) -> bool:
        """
        导航到通讯录页面并进入群组列表

        步骤:
        1. 返回消息列表首页
        2. 点击底部"联系人"Tab
        3. 点击"群组"入口图片
        4. 等待群组列表加载

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 打开通讯录群组列表")
        self._ensure_message_page()
        time.sleep(0.5)
        self.go_to_contacts()
        time.sleep(1)
        self.click_text("群组", timeout=10)
        time.sleep(1.5)
        self.find_text_by_ocr("群组", timeout=5)
        logger.info("✅ 已进入通讯录群组列表")
        return True

    def enter_group_batch_manage(self) -> bool:
        """
        在群组列表页点击"批量管理"进入批量操作模式

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 进入批量管理模式")
        self.click_text("批量管理", timeout=5)
        time.sleep(1)
        logger.info("✅ 已进入批量管理模式")
        return True

    def select_group_in_batch(self, group_index: int = 1) -> bool:
        """
        在批量管理模式中点选第N个群组（勾选其复选框）

        批量管理列表每项高度约60px，首项 y 约在300处。

        Args:
            group_index: 要选择的群组序号（从1开始）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📋 [MuMu] 批量管理 - 选择第{group_index}个群组")
        item_y = 300 + (group_index - 1) * 60
        self.tap(270, item_y)
        time.sleep(0.5)
        logger.info(f"✅ 已点击第{group_index}个群组 (y={item_y})")
        return True

    def get_batch_selected_count(self) -> int:
        """
        获取批量管理模式中已选中的群组数量

        OCR 扫描顶部标题区域，解析"已选X项"/"已选X个"文字。

        Returns:
            int: 已选中的群组数量
        """
        import re
        logger.info("📋 [MuMu] 获取批量管理已选数量")
        results = self.ocr_scan_page()
        for item in results:
            text = item.get('text', '')
            m = re.search(r'已选[：:择]*(\d+)', text)
            if m:
                count = int(m.group(1))
                logger.info(f"✅ 已选数量: {count}")
                return count
        logger.info("未找到'已选'文字，返回0")
        return 0

    def verify_batch_bottom_buttons(self) -> dict:
        """
        验证批量管理模式底部按钮是否存在

        Returns:
            dict: {'select_all': bool, 'exit_group': bool, 'dissolve_group': bool}
        """
        logger.info("📋 [MuMu] 验证批量管理底部按钮")
        results = self.ocr_scan_page()
        texts = {item.get('text', '') for item in results}
        buttons = {
            'select_all': any('全选' in t for t in texts),
            'exit_group': any('退出群组' in t for t in texts),
            'dissolve_group': any('解散群组' in t for t in texts),
        }
        logger.info(f"✅ 底部按钮状态: {buttons}")
        return buttons

    def exit_group_batch_manage(self) -> bool:
        """
        退出批量管理模式（点击"取消"按钮）

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 退出批量管理模式")
        pos = self.find_text_by_ocr("取消", timeout=3)
        if pos:
            self.tap(pos[0], pos[1])
        else:
            self.press_back()
        time.sleep(1)
        logger.info("✅ 已退出批量管理模式")
        return True

    def batch_select_all_groups(self) -> bool:
        """
        在批量管理模式中点击"全选"按钮

        Returns:
            bool: 操作是否成功
        """
        logger.info("📋 [MuMu] 批量管理 - 点击全选")
        self.click_text("全选", timeout=5)
        time.sleep(0.5)
        logger.info("✅ 已点击全选")
        return True

    # ==================== 会话设置（会话盒子 / 会话分组）====================

    def _enter_conversation_settings(self, conversation_name: str) -> bool:
        """
        从消息列表进入任意会话的聊天设置页面

        支持群聊、服务号等各类会话。
        步骤:
        1. 在消息列表用 OCR 找到目标会话并点击进入
        2. 点击顶部标题（聊天标题栏）进入聊天设置

        Args:
            conversation_name: 会话名称关键词

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"⚙️ [MuMu] 进入会话设置页: {conversation_name}")
        self._ensure_message_page()
        time.sleep(0.5)

        # 在消息列表 OCR 找到目标会话
        pos = self.find_text_by_ocr(conversation_name, timeout=5)
        if pos is None:
            # 向下滑动查找
            for _ in range(3):
                self.swipe_up(300)
                time.sleep(0.5)
                pos = self.find_text_by_ocr(conversation_name, timeout=3)
                if pos:
                    break

        if pos is None:
            # 兜底：通过搜索功能导航进入会话
            logger.info(f"🔍 消息列表滚动未找到 '{conversation_name}'，改用搜索导航")
            self._ensure_message_page()
            self.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)
            time.sleep(0.5)
            self.click_image(SELECT_SEARCH, dx=10)
            self.input_text(conversation_name)
            time.sleep(1.5)
            # 切到群Tab过滤结果（限定顶部Tab区域 y<160，避免误点群名）
            try:
                tab_items = self.ocr_scan_page()
                tab_pos = next(
                    (it for it in tab_items if it['text'] == '群' and it['cy'] < 160),
                    None,
                )
                if tab_pos:
                    self.tap(tab_pos['cx'], tab_pos['cy'])
                    time.sleep(1)
            except Exception:
                pass
            # 在搜索结果区（y > 120）找第一个包含关键词的条目，避免误点搜索栏
            items = self.ocr_scan_page()
            result_item = next(
                (it for it in items if it['cy'] > 120 and conversation_name in it['text']),
                None,
            )
            if result_item is None:
                # 关键词未出现在结果文字里（群名显示为成员名），取 y>150 第一个条目
                result_item = next((it for it in items if it['cy'] > 150), None)
            assert result_item is not None, f"搜索结果中未找到会话 '{conversation_name}'"
            self.tap(result_item['cx'], result_item['cy'])
            time.sleep(2)
            # 进入聊天后直接点标题栏（y≈60）进入设置
            self.tap(270, 60)
            time.sleep(2)
            logger.info(f"✅ 已进入会话设置页（搜索路径）: {conversation_name}")
            return True

        assert pos is not None, f"消息列表中未找到会话 '{conversation_name}'"
        self.tap(pos[0], pos[1])
        time.sleep(2)

        # 点击聊天顶部标题栏区域（群名/服务号名在顶部中央, y≈60）
        title_pos = self.find_text_by_ocr(conversation_name, timeout=5)
        if title_pos and title_pos[1] < 120:
            self.tap(title_pos[0], title_pos[1])
        else:
            self.tap(270, 60)
        time.sleep(2)

        logger.info(f"✅ 已进入会话设置页: {conversation_name}")
        return True

    def add_to_session_box(self, conversation_name: str) -> bool:
        """
        将指定会话添加到会话盒子

        通过搜索进入会话 → 设置页 → 开启"添加到会话盒子"开关。
        步骤:
        1. 搜索目标会话并进入聊天窗口
        2. 点击顶部标题进入聊天设置页
        3. 下滑找到"添加到会话盒子"开关并开启
        4. 返回消息列表

        Args:
            conversation_name: 会话名称（搜索关键词，如联系人名/群名）

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📦 [MuMu] 添加到会话盒子: {conversation_name}")

        # 1. 进入会话设置页（内部会先搜索/定位会话再进设置）
        self._enter_conversation_settings(conversation_name)

        # 2. 下滑找到"添加到会话盒子"/"会话盒子"开关
        pos = None
        for _ in range(5):
            pos = self.find_text_by_ocr("会话盒子", timeout=2)
            if pos:
                break
            self.swipe(270, 700, 270, 400, duration=0.3)
            time.sleep(0.5)
        assert pos is not None, "会话设置页中未找到'添加到会话盒子'选项"

        # 3. 点击开关（开关在文字右侧）
        self.tap(480, pos[1])
        time.sleep(1)

        # 4. 返回消息列表
        self.return_to_message_list()
        logger.info(f"✅ 已将 '{conversation_name}' 添加到会话盒子")
        return True

    def remove_from_session_box(self, conversation_name: str) -> bool:
        """
        将指定会话从会话盒子中移除

        通过进入会话盒子 → 点击目标会话 → 设置页 → 关闭"添加到会话盒子"开关。
        步骤:
        1. 进入会话盒子页面
        2. 点击目标会话进入聊天窗口
        3. 点击顶部标题进入聊天设置页
        4. 下滑找到"添加到会话盒子"开关并关闭
        5. 返回消息列表

        Args:
            conversation_name: 会话名称

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📤 [MuMu] 从会话盒子移除: {conversation_name}")

        # 1. 进入会话盒子页面
        self.open_session_box()

        # 2. 点击目标会话进入聊天页
        pos = self.find_text_by_ocr(conversation_name, timeout=10)
        assert pos is not None, f"未在会话盒子中找到会话 '{conversation_name}'"
        self.tap(pos[0], pos[1])
        time.sleep(2)

        # 3. 点击顶部标题进入聊天设置页
        title_pos = self.find_text_by_ocr(conversation_name, timeout=5)
        if title_pos and title_pos[1] < 120:
            self.tap(title_pos[0], title_pos[1])
        else:
            self.tap(270, 60)
        time.sleep(2)

        # 4. 下滑找到"添加到会话盒子"开关并关闭
        pos = None
        for _ in range(5):
            pos = self.find_text_by_ocr("会话盒子", timeout=2)
            if pos:
                break
            self.swipe(270, 700, 270, 400, duration=0.3)
            time.sleep(0.5)
        assert pos is not None, "会话设置页中未找到'添加到会话盒子'选项"

        self.tap(480, pos[1])
        time.sleep(1)

        # 5. 返回消息列表
        self.return_to_message_list()
        logger.info(f"✅ 已将 '{conversation_name}' 从会话盒子移除")
        return True

    def add_conversation_to_group(self, conversation_name: str, group_name: str) -> bool:
        """
        将指定会话添加到某会话分组

        步骤:
        1. 进入会话聊天设置页
        2. 向下滑动找到"会话分组"入口并点击
        3. 在分组列表中找到目标分组名，点击其右侧"+"

        Args:
            conversation_name: 会话名称关键词
            group_name: 目标分组名称

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📁 [MuMu] 添加会话到分组: {conversation_name} -> {group_name}")
        self._enter_conversation_settings(conversation_name)

        # 向下滑动查找"会话分组"入口，用 region 排除顶部标题栏（防止匹配群名中的"会话分组"）
        _SETTINGS_REGION = (0, 120, 540, 840)
        pos = None
        for _ in range(5):
            pos = self.find_text_by_ocr("会话分组", timeout=3, region=_SETTINGS_REGION)
            if pos:
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert pos is not None, "聊天设置中未找到'会话分组'入口"
        self.tap(pos[0], pos[1])
        time.sleep(1.5)

        # 在分组选择页找到目标分组名，点击其右侧"+"（偏移约+150）
        group_pos = self.find_text_by_ocr(group_name, timeout=5)
        if group_pos is None:
            # 分组不存在，点击右上角"+"新建分组
            logger.info(f"⚠️ 会话分组 '{group_name}' 不存在，自动创建")
            self._adb_tap(408, 72)
            time.sleep(1)
            self.input_text(group_name)
            time.sleep(0.3)
            confirm_pos = self.find_text_by_ocr("确定", timeout=3)
            if confirm_pos:
                self.tap(confirm_pos[0], confirm_pos[1])
            else:
                self._run_adb_command("shell", "input", "keyevent", "66")
            time.sleep(1)
            group_pos = self.find_text_by_ocr(group_name, timeout=5)
        assert group_pos is not None, f"分组列表中未找到分组 '{group_name}'"
        self.tap(group_pos[0], group_pos[1])  # 点击分组名即可选中（知识库描述）
        time.sleep(1)

        self.return_to_message_list()
        logger.info(f"✅ 已将 '{conversation_name}' 添加到分组 '{group_name}'")
        return True

    def remove_conversation_from_group(self, conversation_name: str, group_name: str) -> bool:
        """
        将指定会话从某会话分组中移除

        步骤:
        1. 进入会话聊天设置页
        2. 向下滑动找到"会话分组"入口并点击
        3. 在分组列表中找到已选中的目标分组名，点击其右侧"×"取消

        Args:
            conversation_name: 会话名称关键词
            group_name: 要移除的分组名称

        Returns:
            bool: 操作是否成功
        """
        logger.info(f"📁 [MuMu] 从分组移除会话: {conversation_name} <- {group_name}")
        self._enter_conversation_settings(conversation_name)

        _SETTINGS_REGION = (0, 120, 540, 840)
        pos = None
        for _ in range(5):
            pos = self.find_text_by_ocr("会话分组", timeout=3, region=_SETTINGS_REGION)
            if pos:
                break
            self.swipe_up(300)
            time.sleep(0.5)

        assert pos is not None, "聊天设置中未找到'会话分组'入口"
        self.tap(pos[0], pos[1])
        time.sleep(1.5)

        # 在分组选择页找已选中的分组名，点击即可取消选中（单选模式下再点一次移除）
        group_pos = self.text_exists(group_name, timeout=5)
        self.tap(group_pos[0], group_pos[1])
        time.sleep(1)

        self.return_to_message_list()
        logger.info(f"✅ 已将 '{conversation_name}' 从分组 '{group_name}' 移除")
        return True
