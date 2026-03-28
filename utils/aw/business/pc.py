"""
PC (Windows) 端业务方法

包含 Windows 桌面端 POPO 应用的完整业务操作流程。
UI 流程、检查图片、操作步骤均为 PC 端专属。
"""
import logging

from utils.aw.business.common import CommonBusiness
from utils.aw.driver.base_driver import BasePlatformDriver

logger = logging.getLogger(__name__)


class PCBusiness(CommonBusiness):
    """
    PC (Windows) 端业务类

    继承链: PCBusiness → CommonBusiness → AWBase
    """

    def __init__(self, driver: BasePlatformDriver):
        super().__init__(driver)

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
        logger.info(f"✅ [PC] 登录完成: {uid}")

    def logout(self) -> bool:
        """
        PC 端退出登录流程

        TODO: 需要根据实际 PC 端 UI 补充完整流程
        """
        logger.info("🚪 [PC] 开始退出登录")

        # TODO: 根据 PC 端实际 UI 实现退出登录步骤
        logger.info("✅ [PC] 退出登录完成")
        return True

    # ==================== 搜索 ====================

    def search_contact(self, keyword: str) -> bool:
        """搜索联系人"""
        logger.info(f"🔍 搜索联系人: '{keyword}'")

        self.activate()

        search_pos = self.find_text_by_ocr("搜索", timeout=8)
        if search_pos is None:
            search_pos = self.find_text_by_ocr("Search", timeout=5)
        assert search_pos is not None, "❌ 未找到搜索框"

        self.tap(search_pos[0], search_pos[1])
        self.sleep(0.5)

        self.clear_input()
        self.input_text(keyword)
        self.sleep(1.5)

        logger.info(f"✅ 搜索完成: '{keyword}'")
        return True

    def close_search(self) -> bool:
        """关闭搜索框"""
        self.press_key('escape')
        self.sleep(0.3)
        logger.info("🔙 已关闭搜索框")
        return True

    # ==================== 消息 ====================

    def send_message(self, contact: str, message: str) -> bool:
        """搜索联系人并发送消息"""
        logger.info(f"📤 向 '{contact}' 发送消息: '{message}'")

        self.search_contact(contact)

        contact_pos = self.find_text_by_ocr(contact, timeout=5)
        assert contact_pos is not None, f"❌ 搜索结果中未找到: '{contact}'"
        self.tap(contact_pos[0], contact_pos[1])
        self.sleep(1.0)

        input_pos = self.find_text_by_ocr("发送", timeout=5)
        if input_pos:
            self.tap(input_pos[0] - 200, input_pos[1])
            self.sleep(0.3)

        self.input_text(message)
        self.sleep(0.3)
        self.press_key('enter')
        self.sleep(0.5)

        logger.info("✅ 消息已发送")
        return True
