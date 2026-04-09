"""
测试用例: 搜索联系人并发送消息功能测试
"""
from conftest import BaseTest


class TestSendMessage(BaseTest):
    """搜索联系人并发送消息功能测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_search_contact_and_send_message(self):
        """
        测试场景: 搜索联系人并发送消息

        步骤:
        1. 激活POPO PC窗口
        2. 搜索联系人 grp.popoqa93
        3. 点击搜索结果中的联系人
        4. 在聊天窗口输入消息
        5. 发送消息
        """
        self.userA.aw.send_message("grp.popoqa93", "这是一条自动化测试消息")
        self.userA.create_team()

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA') and self.userA.is_logged_in:
            self.userA.logout()
