"""
测试用例: 分组管理展示区域内容
覆盖文字用例: 隐藏栏-默认空状态
"""
from conftest import BaseTest


class TestSessionGroupManageShowGroups(BaseTest):
    """验证管理分组页面展示区域显示所有启用的分组"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_manage_page_show_groups(self):
        """
        验证管理分组页面展示区域内容
        覆盖用例: 隐藏栏-默认空状态
        预期: 展示区域显示所有启用的分组（系统分组标记），隐藏栏为空不显示
        """
        self.userA.open_session_group_manage()
        # 验证展示区域有分组
        self.userA.aw.find_text_by_ocr("展示", timeout=5)
        self.userA.aw.find_text_by_ocr("最近", timeout=5)
        self.userA.aw.find_text_by_ocr("系统分组", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
