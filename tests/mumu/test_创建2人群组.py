"""
测试用例: 创建群组功能测试
"""
from conftest import BaseTest


class TestCreateTeam(BaseTest):
    """创建群组功能测试类"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_create_team(self):
        """
        测试场景: 创建群组并验证

        步骤:
        1. 点击会话列表的加号按钮
        2. 点击创建群聊
        3. 搜索并选择群成员
        4. 确认创建
        5. 验证群聊创建成功（页面出现"发起群聊"、"并邀请"、"加入群聊"文案）
        """
        self.userA.create_team()
        self.userA.delete_team()

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA') and self.userA.is_logged_in:
            self.userA.logout()
