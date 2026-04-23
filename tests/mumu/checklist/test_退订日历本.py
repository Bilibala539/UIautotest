"""
测试用例: 退订日历本
探索来源: AI自主探索POPO App日历功能生成
"""
from conftest import BaseTest


class TestUnsubscribeCalendarBook(BaseTest):
    """退订日历本测试类"""

    def setup(self):
        """测试前初始化 - 先订阅一个日历本用于退订"""
        self.userA = self.users("userA")
        self.userA.subscribe_calendar_book("孟龄钊")

    def test_unsubscribe_calendar_book(self):
        """
        测试退订日历本

        步骤:
        1. 展开日历侧边栏
        2. 点击订阅日历本右侧的...按钮
        3. 退订日历本

        预期结果:
        可以正常退订日历本，日历本从侧边栏移除
        """
        result = self.userA.unsubscribe_calendar_book("孟龄钊")
        assert result, "退订日历本应该成功"

    def teardown(self):
        """测试后清理"""
        pass
