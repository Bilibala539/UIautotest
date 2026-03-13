"""
测试用例: 创建群组
"""
import pytest


class TestCreateGroup:
    """测试创建群组功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_create_group(self):
        """
        测试创建群组功能
        
        步骤:
        1. 确保在消息tab页
        2. 点击右上角"+"按钮
        3. 点击"创建群组"
        4. 选择群成员（悠哈哈、111）
        5. 点击确定创建群组
        6. 验证群组创建成功（进入群聊界面）
        """
        # 创建群组，选择成员
        result = self.userA.aw.create_group(["悠哈哈", "111"])
        assert result, "群组创建失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
