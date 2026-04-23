"""
测试用例: 订阅日历本
探索来源: AI自主探索POPO App日历功能生成
"""
import logging
from conftest import BaseTest

logger = logging.getLogger(__name__)


class TestSubscribeCalendarBook(BaseTest):
    """订阅日历本测试类"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_subscribe_calendar_book(self):
        """
        测试订阅日历本

        步骤:
        1. 展开日历侧边栏
        2. 点击搜索框
        3. 搜索日历本，点击订阅

        预期结果:
        可以正常订阅日历本，并展示在侧边栏
        """
        result = self.userA.subscribe_calendar_book("孟龄钊")
        assert result, "订阅日历本应该成功"

    def teardown(self):
        """测试后清理 - 退订日历本"""
        try:
            self.userA.unsubscribe_calendar_book("孟龄钊")
        except Exception as e:
            logger.warning(f"⚠️ teardown 清理失败（不影响测试结果）: {e}")
