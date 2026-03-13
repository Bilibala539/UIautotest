"""
测试用例: 切换群消息提醒
"""
import pytest


class TestToggleGroupNotification:
    """测试切换群消息提醒功能"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_toggle_group_notification(self):
        """
        测试切换群消息提醒功能
        
        步骤:
        1. 进入群聊"POPO通知服务测试"
        2. 打开群设置
        3. 滑动到消息提醒位置
        4. 关闭消息提醒
        5. 再次开启消息提醒
        6. 验证操作成功
        """
        # 先进入群聊并打开群设置
        self.userA.aw.enter_group("POPO通知服务测试")
        self.userA.aw.open_group_settings()
        
        # 关闭消息提醒
        result = self.userA.aw.toggle_group_notification(enable=False)
        assert result, "关闭群消息提醒失败"
        
        # 再次开启
        result = self.userA.aw.toggle_group_notification(enable=True)
        assert result, "开启群消息提醒失败"

    def teardown(self):
        """
        测试后清理
        - 用户退登
        """
        if hasattr(self, 'userA'):
            self.userA.logout()
