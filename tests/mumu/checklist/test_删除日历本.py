"""
测试用例: 删除日历本
探索来源: AI自主探索POPO App日历功能生成
"""
from conftest import BaseTest


class TestDeleteCalendarBook(BaseTest):
    """删除日历本测试类"""

    def setup(self):
        """测试前初始化 - 先创建一个日历本用于删除"""
        self.userA = self.users("userA")
        self.userA.create_calendar_book("DeleteTestCal")

    def test_delete_calendar_book(self):
        """
        测试删除日历本

        步骤:
        1. 展开日历侧边栏
        2. 点击日历本右侧...按钮
        3. 点击日历设置，删除日历本

        预期结果:
        可以正常删除日历本，日历本从侧边栏移除
        """
        result = self.userA.delete_calendar_book("DeleteTestCal")
        assert result, "删除日历本应该成功"

    def teardown(self):
        """测试后清理"""
        pass
