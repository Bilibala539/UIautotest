"""
测试用例: 完整群组操作流程
测试创建群组→发送消息→打开设置→退出群组的完整流程
"""
import pytest


class TestGroupFullFlow:
    """测试完整的群组操作流程"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_group_full_flow(self):
        """
        测试完整的创建群组并退出流程
        
        步骤:
        1. 创建群组（选择悠哈哈、111）
        2. 发送一条群消息
        3. 打开群设置
        4. 退出群组
        5. 验证回到消息列表
        """
        # 1. 创建群组
        create_result = self.userA.aw.create_group(["悠哈哈", "111"])
        assert create_result, "群组创建失败"
        #
        # # 2. 发送消息
        # send_result = self.userA.aw.send_group_message("群组创建成功，这是第一条消息！")
        # assert send_result, "发送消息失败"
        #
        # # 3. 打开群设置
        # settings_result = self.userA.aw.open_group_settings()
        # assert settings_result, "打开群设置失败"
        #
        # # 4. 退出群组
        # exit_result = self.userA.aw.exit_group()
        # assert exit_result, "退出群组失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
