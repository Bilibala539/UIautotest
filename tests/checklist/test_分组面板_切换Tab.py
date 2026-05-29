"""
测试用例: 分组面板切换Tab
覆盖文字用例: 切换tab
"""
import pytest
from conftest import BaseTest


class TestSessionGroupPanelSwitchTab(BaseTest):
    """验证切换分组Tab，显示该tab下的会话列表"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    @pytest.mark.parametrize("tab_name", ["@我", "未读", "待处理", "最近"])
    def test_switch_group_tab(self, tab_name):
        """
        验证切换分组Tab
        覆盖用例: 切换tab
        预期: 可以切换各个tab栏，并显示该tab下的会话列表
        """
        self.userA.switch_session_group_tab(tab_name)
        # 切换回最近tab
        if tab_name != "最近":
            self.userA.switch_session_group_tab("最近")

    def teardown(self):
        """测试后清理"""
        pass
