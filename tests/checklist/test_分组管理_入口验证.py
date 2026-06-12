"""
测试用例: 分组管理入口验证
覆盖文字用例: 入口1 (点击会话分组栏-更多-管理)
"""
from conftest import BaseTest


class TestSessionGroupManageEntry(BaseTest):
    """验证进入分组管理页面，显示管理分组标题、展示区域和分组Tab开关"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_enter_manage_page(self):
        """
        验证进入分组管理页面
        覆盖用例: 入口1
        步骤: 点击会话分组栏-更多-管理
        预期: 进入分组管理页面，显示"管理分组"标题、展示区域和分组Tab开关
        """
        self.userA.open_session_group_manage()
        # 验证管理分组页面元素
        self.userA.aw.find_text_by_ocr("管理分组", timeout=5)
        self.userA.aw.find_text_by_ocr("显示会话分组Tab", timeout=5)
        self.userA.aw.find_text_by_ocr("展示", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
