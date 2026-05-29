"""
测试用例: 分组面板打开验证
覆盖文字用例: 面板展开的显示--PC端设置过
"""
from conftest import BaseTest


class TestSessionGroupPanelOpen(BaseTest):
    """验证打开会话分组面板，显示所有分组、管理按钮、会话盒子和关闭的会话"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_open_session_group_panel(self):
        """
        验证打开会话分组面板
        覆盖用例: 面板展开的显示--PC端设置过
        预期: 展开分组面板，显示所有分组，右上角有管理按钮，下方显示会话盒子和关闭的会话
        """
        self.userA.open_session_group_panel()
        # 验证面板内容: 会话分组标题、管理按钮
        self.userA.aw.find_text_by_ocr("会话分组", timeout=5)
        self.userA.aw.find_text_by_ocr("管理", timeout=5)
        # 验证有会话盒子和关闭的会话入口
        self.userA.aw.find_text_by_ocr("会话盒子", timeout=5)
        self.userA.aw.find_text_by_ocr("关闭的会话", timeout=5)
        # 关闭面板恢复初始状态
        self.userA.close_session_group_panel()

    def teardown(self):
        """测试后清理"""
        pass
