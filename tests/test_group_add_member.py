"""
测试用例: 添加群成员
"""
import pytest


class TestAddGroupMember:
    """测试添加群成员功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_add_group_member(self):
        """
        测试添加群成员功能
        
        步骤:
        1. 进入群聊"POPO通知服务测试"
        2. 打开群设置
        3. 点击"添加"按钮
        4. 选择要添加的成员（黑岩）
        5. 点击确定
        6. 验证添加成功
        """
        # 先进入群聊并打开群设置
        self.userA.aw.enter_group("POPO通知服务测试")
        self.userA.aw.open_group_settings()
        
        # 添加成员
        result = self.userA.aw.add_group_member(["黑岩"])
        assert result, "添加群成员失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
