"""
测试用例: 面板展开的显示
功能点: 新增会话分组模块
操作步骤: 点击分组栏右侧按钮展开面板
预期结果: 展开分组面板，显示所有分组，下方显示会话盒子
"""
from conftest import BaseTest


class TestGroupPanelDisplay(BaseTest):
    """面板展开的显示验证"""

    def setup(self):
        self.userA = self.users("userA")

    def test_group_panel_display(self):
        """
        步骤:
        1. 在消息列表页点击展开按钮打开会话分组面板
        2. 验证面板已展开（open_session_group_panel 内部通过 image_exists 校验）
        """
        result = self.userA.open_session_group_panel()
        assert result, "会话分组面板展开失败"

    def teardown(self):
        """收起面板"""
        self.userA.close_session_group_panel()
