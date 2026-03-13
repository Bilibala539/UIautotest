"""
测试用例: 邮箱登录流程
"""
from time import sleep

import pytest


class Test01:
    """测试使用邮箱登录的完整流程"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_01(self):
        """
        步骤:
        1. 等待登录页面出现
        2. 点击邮箱Tab
        3. 点击邮箱输入框，输入邮箱
        4. 点击密码输入框，输入密码
        5. 勾选协议复选框
        6. 点击登录按钮
        7. 验证登录成功
        """

    def teardown(self):
        """测试后清理"""
        self.userA.logout()
