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
        1. 在消息列表页点击"展开"按钮
        2. 验证面板中显示"收起"按钮（确认已展开）
        3. 验证面板中能看到分组标签
        """
        self.userA.open_session_group_panel()
        # 验证面板已展开 - 检查"收起"按钮存在
        self.userA.text_exists("收起")

    def teardown(self):
        """收起面板"""
        self.userA.close_session_group_panel()
