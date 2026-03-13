"""
测试用例: 创建群组功能入口
"""
from time import sleep

import pytest


class TestCreateGroupEntry:
    """测试创建群组功能入口"""

    def setup(self):
        """
        测试前初始化
        - 实例化用户
        - 用户登录
        """
        self.userA = self.users("userA")
        self.userA.login()

    def test_open_create_group(self):
        """
        测试场景: 通过顶部添加按钮打开创建群组功能

        步骤:
        1. 确认当前在消息页面
        2. 点击顶部添加按钮(+)，弹出功能菜单
        3. 点击"创建群组"选项
        4. 验证进入创建群组页面
        
        预期结果: 进入创建群组页面，可以选择群成员
        """
        # 步骤1: 确认当前在消息页面
        print("当前在消息页面")
        sleep(1)

        # 步骤2: 点击顶部添加按钮(+)，弹出功能菜单
        print("点击添加按钮")
        self.userA.device.tap(490, 70)
        sleep(1)

        # 步骤3: 点击"创建群组"选项
        print("点击创建群组")
        self.userA.device.tap(378, 303)
        sleep(1.5)

        # 步骤4: 验证进入创建群组页面
        # TODO: 可以通过OCR识别"创建群组"标题验证
        print("验证进入创建群组页面")
        sleep(1)

    def teardown(self):
        """
        测试后清理
        - 返回消息页面
        - 用户退登
        """
        # 按返回键回到消息页面
        self.userA.device.keyevent(4)
        sleep(1)
        self.userA.logout()
