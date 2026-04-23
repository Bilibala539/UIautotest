"""
PC (Windows) 端业务方法

包含 Windows 桌面端 POPO 应用的完整业务操作流程。
UI 流程、检查图片、操作步骤均为 PC 端专属。

与安卓端的关键差异:
- 无底部导航栏，使用侧边栏/菜单栏导航
- 无返回键，使用 Escape 或关闭按钮
- 窗口大小不固定，搜索区域需动态计算
- 支持键盘快捷键（Ctrl+F搜索、Ctrl+Enter发送等）
- 输入使用剪贴板(Ctrl+V)，不受输入法影响
"""
import logging
import subprocess
import time

from utils.aw.business.common import CommonBusiness
from utils.aw.driver.base_driver import BasePlatformDriver
from utils.aw.search_region import Normal

logger = logging.getLogger(__name__)

# POPO PC端进程名
POPO_PC_PROCESS = "POPO.exe"


class PCBusiness(CommonBusiness):
    """
    PC (Windows) 端业务类

    继承链: PCBusiness → CommonBusiness → AWBase
    """

    def __init__(self, driver: BasePlatformDriver):
        super().__init__(driver)

    # ==================== 应用控制 ====================

    def open_app(self):
        """
        激活 POPO PC 窗口并确保在消息列表页

        步骤:
        1. 激活 POPO 窗口
        2. 检查是否已在消息列表页
        3. 如果不在，尝试按 Escape 回到消息页
        4. 处理可能出现的弹窗

        TODO: 需要根据实际 PC 端 UI 补充页面判断逻辑
        """
        logger.info("📱 [PC] 启动 POPO 应用")
        self.activate()
        self.sleep(1)

        # TODO: 根据 PC 端实际 UI 判断是否在消息列表页
        # 例如: if self.find_image(PC_MESSAGE_TAB_ACTIVE, timeout=2):

        logger.info("✅ [PC] POPO 已激活")

    def close_app(self):
        """
        关闭 POPO PC 窗口（不退出登录）

        PC端关闭窗口通常不退出登录，只是最小化或隐藏窗口。
        """
        logger.info("📱 [PC] 关闭 POPO 应用")
        # PC端通常不需要强制关闭，最小化即可
        # 如果需要关闭，可以使用 Alt+F4
        # self.press_key('alt+F4')  # 注意：这会退出应用
        logger.info("✅ [PC] POPO 已关闭")

    def start_app(self):
        """启动 POPO PC 应用进程"""
        logger.info("🚀 [PC] 启动 POPO 进程")
        # TODO: 根据 POPO PC 的实际安装路径配置
        # 示例: subprocess.Popen([r"C:\Program Files\Netease\POPO\POPO.exe"])
        self.sleep(3)
        self.activate()
        logger.info("✅ [PC] POPO 进程已启动")

    def stop_app(self) -> bool:
        """停止 POPO PC 应用进程"""
        logger.info("📱 [PC] 停止 POPO 进程")
        try:
            subprocess.run(["taskkill", "/F", "/IM", POPO_PC_PROCESS],
                           capture_output=True, timeout=10)
            self.sleep(1)
            logger.info("✅ [PC] POPO 进程已停止")
            return True
        except subprocess.TimeoutExpired:
            logger.error("❌ 停止 POPO 进程超时")
            return False
        except Exception as e:
            logger.error(f"❌ 停止 POPO 进程失败: {e}")
            return False

    # ==================== 登录 / 退登 ====================

    def login(self, uid: str, password: str):
        """
        PC 端登录流程

        前提: POPO PC客户端已安装并运行，处于登录页面。

        步骤:
        1. 激活 POPO 窗口
        2. 等待登录页面
        3. 输入邮箱
        4. 输入密码
        5. 点击登录按钮
        6. 等待登录完成

        TODO: 需要根据实际 PC 端 UI 补充完整流程
        """
        logger.info(f"🔐 [PC] 开始登录: {uid}")

        self.activate()
        self.sleep(1)

        # TODO: 根据 PC 端实际 UI 实现登录步骤
        # 以下是示意流程，需要截取 PC 端 UI 元素图片后补充
        # 1. 检查是否在登录页面
        #    self.image_exists(PC_LOGIN_PAGE_INDICATOR, timeout=10)
        # 2. 输入邮箱
        #    self.click_image(PC_LOGIN_EMAIL_INPUT)
        #    self.clear_input()
        #    self.input_text(uid)
        # 3. 输入密码
        #    self.click_image(PC_LOGIN_PASSWORD_INPUT)
        #    self.clear_input()
        #    self.input_text(password)
        # 4. 点击登录
        #    self.click_image(PC_LOGIN_ENTER)
        # 5. 等待进入消息列表页
        #    self.image_exists(PC_MESSAGE_TAB_ACTIVE, timeout=15)

        logger.info(f"✅ [PC] 登录完成: {uid}")

    def logout(self) -> bool:
        """
        PC 端退出登录流程

        TODO: 需要根据实际 PC 端 UI 补充完整流程
        """
        logger.info("🚪 [PC] 开始退出登录")

        # TODO: 根据 PC 端实际 UI 实现退出登录步骤
        # 1. 确保在消息列表页
        # 2. 打开设置/菜单
        # 3. 点击退出登录
        # 4. 确认退出
        # 5. 验证回到登录页

        logger.info("✅ [PC] 退出登录完成")
        return True

    # ==================== 弹窗处理 ====================

    def pop_not_allowed(self):
        """处理不允许的弹窗（点击取消/关闭）"""
        # PC端可能有Windows通知弹窗、更新提示等
        # 尝试按 Escape 关闭可能的弹窗
        self.press_key('escape')
        self.sleep(0.3)

    def pop_allowed(self):
        """处理允许的弹窗（点击确定/允许）"""
        pass

    # ==================== 搜索 ====================

    def search_contact(self, keyword: str) -> bool:
        """
        搜索联系人

        步骤:
        1. 激活窗口
        2. 点击搜索框或使用 Ctrl+F
        3. 输入关键词
        4. 等待搜索结果

        Args:
            keyword: 搜索关键词

        Returns:
            bool: 搜索是否成功
        """
        logger.info(f"🔍 [PC] 搜索联系人: '{keyword}'")

        self.activate()

        # 尝试找到搜索框
        search_pos = self.find_text_by_ocr("搜索", timeout=8)
        if search_pos is None:
            search_pos = self.find_text_by_ocr("Search", timeout=5)
        assert search_pos is not None, "❌ 未找到搜索框"

        self.tap(search_pos[0], search_pos[1])
        self.sleep(0.5)

        self.clear_input()
        self.input_text(keyword)
        self.sleep(1.5)

        logger.info(f"✅ [PC] 搜索完成: '{keyword}'")
        return True

    def close_search(self) -> bool:
        """关闭搜索框"""
        self.press_key('escape')
        self.sleep(0.3)
        logger.info("🔙 [PC] 已关闭搜索框")
        return True

    # ==================== 消息 ====================

    def send_message(self, contact: str, message: str) -> bool:
        """
        搜索联系人并发送消息

        步骤:
        1. 搜索联系人
        2. 点击搜索结果
        3. 输入消息
        4. 发送消息（Ctrl+Enter 或点击发送按钮）

        Args:
            contact: 联系人名称或账号
            message: 消息内容

        Returns:
            bool: 发送是否成功
        """
        logger.info(f"📤 [PC] 向 '{contact}' 发送消息: '{message}'")

        self.search_contact(contact)

        contact_pos = self.find_text_by_ocr(contact, timeout=5)
        assert contact_pos is not None, f"❌ 搜索结果中未找到: '{contact}'"
        self.tap(contact_pos[0], contact_pos[1])
        self.sleep(1.0)

        # 点击输入框区域
        input_pos = self.find_text_by_ocr("发送", timeout=5)
        if input_pos:
            self.tap(input_pos[0] - 200, input_pos[1])
            self.sleep(0.3)

        self.input_text(message)
        self.sleep(0.3)

        # PC端使用 Enter 发送消息
        self.press_key('enter')
        self.sleep(0.5)

        logger.info("✅ [PC] 消息已发送")
        return True

    # ==================== 页面导航 ====================

    def go_to_messages(self) -> bool:
        """
        导航到消息页面

        PC端: 点击左侧导航栏的"消息"入口
        """
        logger.info("💬 [PC] 进入消息页面")
        return self.click_text("消息", timeout=5)

    def go_to_contacts(self) -> bool:
        """
        导航到通讯录页面

        PC端: 点击左侧导航栏的"通讯录"入口
        """
        logger.info("📇 [PC] 进入通讯录页面")
        return self.click_text("通讯录", timeout=5)

    def go_to_settings(self) -> bool:
        """
        导航到设置页面

        PC端: 通常通过菜单或头像下拉进入设置
        """
        logger.info("⚙️ [PC] 进入设置页面")
        return self.click_text("设置", timeout=5)

    # ==================== PC端特有操作 ====================

    def hotkey(self, *keys) -> bool:
        """
        发送组合快捷键

        Args:
            *keys: 按键组合，如 ('ctrl', 'f'), ('ctrl', 'shift', 'a')

        Returns:
            bool: 是否成功
        """
        import pyautogui
        self.activate()
        self.sleep(0.2)
        pyautogui.hotkey(*keys)
        logger.info(f"⌨️ [PC] 快捷键: {'+'.join(keys)}")
        self.sleep(0.3)
        return True

    def right_click(self, x: int, y: int) -> bool:
        """
        右键点击窗口内坐标

        Args:
            x, y: 窗口内坐标

        Returns:
            bool: 是否成功
        """
        screen_coords = self.driver.to_screen_coords(x, y)
        if not screen_coords:
            return False

        import pyautogui
        pyautogui.rightClick(screen_coords[0], screen_coords[1])
        logger.info(f"👆 [PC] 右键点击 ({x}, {y})")
        self.sleep(0.3)
        return True

    def right_click_text(self, text: str, timeout: int = 10,
                         region=Normal.ALL) -> bool:
        """
        OCR 找到文字后右键点击

        Args:
            text: 要查找的文字
            timeout: 超时时间
            region: 搜索区域

        Returns:
            bool: 是否成功
        """
        pos = self.find_text_by_ocr(text, timeout=timeout, region=region)
        assert pos is not None, f"未找到文字 '{text}'"
        return self.right_click(pos[0], pos[1])

    def right_click_image(self, image: str, threshold: float = 0.8,
                          timeout: int = 10,
                          region=Normal.ALL) -> bool:
        """
        模板匹配找到图片后右键点击

        Args:
            image: 模板图片文件名或绝对路径
            threshold: 匹配阈值
            timeout: 超时时间
            region: 搜索区域

        Returns:
            bool: 是否成功
        """
        pos = self.find_image(image, threshold=threshold, timeout=timeout, region=region)
        assert pos is not None, f"未找到图片 '{image}'"
        return self.right_click(pos[0], pos[1])
