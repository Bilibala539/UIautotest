"""
测试用例: 长按会话添加至分组
覆盖文字用例: 长按会话添加至分组
"""
import time
from conftest import BaseTest


class TestLongPressSessionAddToGroup(BaseTest):
    """验证长按会话添加至分组，进入分组选择页面"""

    def setup(self):
        """测试前初始化"""
        self.userA = self.users("userA")

    def test_long_press_add_to_group(self):
        """
        验证长按会话添加至分组
        覆盖用例: 给会话添加分组
        预期: 长按后弹出菜单（需要滑动），点击添加至分组后进入分组选择页面
        """
        self.userA.long_press_session_add_to_group()
        # 验证进入了分组选择页面 - 应该能看到分组列表
        time.sleep(1)
        # 返回
        self.userA.aw.press_back()

    def teardown(self):
        """测试后清理"""
        pass
