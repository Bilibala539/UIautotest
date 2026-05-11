"""
测试用例: 手动启用工作状态
功能点: 设置工作状态
操作步骤: 在工作状态页面点击任一状态启用
预期结果: 状态被启用
"""
from conftest import BaseTest


class TestEnableWorkStatus(BaseTest):
    """手动启用工作状态"""

    def setup(self):
        self.userA = self.users("userA")

    def test_enable_work_status(self):
        """
        步骤:
        1. 打开工作状态设置页面
        2. 点击"忙碌"状态
        3. 验证状态被启用
        """
        self.userA.open_work_status_page()
        self.userA.enable_work_status("忙碌")

    def teardown(self):
        """关闭工作状态页面"""
        self.userA.close_work_status_page()
