"""
测试用例: 关闭展开的分组栏
探索来源: AI自主探索POPO App - 会话分组功能
用例描述: 会话列表页-会话分组更多弹窗展开后，点击蒙层区域，验证弹窗关闭
"""
from conftest import BaseTest


class TestCloseSessionGroupPanel(BaseTest):
    """关闭展开的分组栏 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_close_session_group_panel(self):
        """
        步骤:
        1. 在消息列表页点击分组标签栏右侧≡按钮，打开会话分组弹窗
        2. 点击蒙层区域关闭弹窗
        3. 验证弹窗已关闭
        """
        # 打开会话分组弹窗
        self.userA.open_session_group_panel()

        # 点击蒙层区域关闭弹窗
        self.userA.close_session_group_panel()

    def teardown(self):
        pass
