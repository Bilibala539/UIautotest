"""
测试用例: 退出群组
"""
import pytest


class TestExitGroup:
    """测试退出群组功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_exit_group(self):
        """
        测试退出群组功能
        
        步骤:
        1. 先创建一个测试群组
        2. 打开群设置
        3. 滑动到页面底部
        4. 点击"退出群组"按钮
        5. 确认退出
        6. 验证退出成功（回到消息列表）
        """
        # 先创建一个测试群组
        self.userA.aw.create_group(["悠哈哈"])
        
        # 退出刚创建的群组
        result = self.userA.aw.exit_group()
        assert result, "退出群组失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
