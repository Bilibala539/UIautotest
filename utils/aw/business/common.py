"""
通用业务方法

通用的业务操作放这里，只维护一份。
MuMuBusiness 继承此类。
"""
import logging

from utils.aw.aw_base import AWBase
from utils.aw.driver.base_driver import BasePlatformDriver

logger = logging.getLogger(__name__)


class CommonBusiness(AWBase):
    """
    通用业务基类

    包含通用的业务方法。
    MuMuBusiness 继承此类。
    """

    def __init__(self, driver: BasePlatformDriver):
        super().__init__(driver)

    # ==================== 窗口 ====================

    def activate(self) -> bool:
        """激活窗口并置于前台"""
        logger.info("📋 激活目标窗口...")
        result = self.driver.focus_window()
        self.sleep(0.5)
        return result

    # ==================== 页面导航 ====================

    def go_to_home(self) -> bool:
        """返回首页"""
        logger.info("🏠 返回首页")
        for _ in range(5):
            self.press_back()
            self.sleep(0.3)
        return True

    def go_to_contacts(self) -> bool:
        """进入联系人页面"""
        logger.info("📇 进入联系人页面")
        return self.click_text("联系人", timeout=5)

    def go_to_messages(self) -> bool:
        """进入消息页面"""
        logger.info("💬 进入消息页面")
        return self.click_text("消息", timeout=5)

    def go_to_settings(self) -> bool:
        """进入设置页面"""
        logger.info("⚙️ 进入设置页面")
        return self.click_text("设置", timeout=5)
