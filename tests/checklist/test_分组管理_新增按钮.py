"""
测试用例: 分组管理新增按钮
覆盖文字用例: 新增分组默认名称"未命名"
"""
from conftest import BaseTest


class TestSessionGroupManageAddButton(BaseTest):
    """验证管理分组页面有+号添加按钮，可用于新增分组"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_manage_page_has_add_button(self):
        """
        验证管理分组页面有+号添加按钮
        覆盖用例: 新增分组默认名称"未命名"（验证入口存在）
        预期: 页面右上角有+号按钮，可用于新增分组
        """
        self.userA.open_session_group_manage()
        # 验证+号按钮存在(在标题栏右侧)
        self.userA.aw.find_text_by_ocr("+", timeout=5)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
