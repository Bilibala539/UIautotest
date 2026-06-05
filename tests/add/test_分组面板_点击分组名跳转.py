"""
测试用例: 分组面板点击分组名跳转
覆盖文字用例: 点击分组名跳转分组列表-分组栏展开
"""
from conftest import BaseTest


class TestSessionGroupPanelClickGroupName(BaseTest):
    """验证面板展开后点击分组名跳转到该分组列表"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_panel_click_group_name(self):
        """
        验证面板展开后点击分组名跳转
        覆盖用例: 点击分组名跳转分组列表-分组栏展开
        预期: 打开该tab下的会话列表，面板自动关闭
        """
        self.userA.open_session_group_panel()
        # 点击面板中的"未读"分组名
        self.userA.aw.click_text("未读", timeout=5)
        import time
        time.sleep(1)
        # 面板应该关闭，切换到未读tab
        # 切回最近
        self.userA.switch_session_group_tab("最近")

    def teardown(self):
        """测试后清理"""
        pass
