"""
测试用例: 设置工作状态的页面展示
功能点: 设置工作状态
操作步骤: 进入设置工作状态页面，查看页面展示
预期结果: 左上角X，列表包含忙碌、会议中、离开等通用状态
"""
from conftest import BaseTest


class TestWorkStatusPageDisplay(BaseTest):
    """设置工作状态的页面展示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_work_status_page_display(self):
        """
        步骤:
        1. 打开侧边栏 → 点击工作状态入口
        2. 验证页面显示"忙碌"
        3. 验证页面显示"会议中"
        """
        self.userA.open_work_status_page()
        # 验证通用状态项存在
        self.userA.text_exists("忙碌")
        self.userA.text_exists("会议中")

    def teardown(self):
        """关闭工作状态页面"""
        self.userA.close_work_status_page()
