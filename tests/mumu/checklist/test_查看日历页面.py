"""
测试用例: 查看日历页面
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
探索来源: explorer_output/screenshots/explore_step1_calendar.png
"""
from conftest import BaseTest


class TestViewCalendar(BaseTest):
    """查看日历页面功能测试"""

    def setup(self):
        self.userA = self.users("userA")

    def test_view_calendar(self):
        """
        测试查看日历页面

        步骤:
        1. 从消息列表页点击底部"日历"Tab
        2. 验证日历会议室页面加载（标题"日历会议室"、UTC时区信息）
        3. 返回消息列表页
        """
        self.userA.view_calendar()

    def teardown(self):
        pass
