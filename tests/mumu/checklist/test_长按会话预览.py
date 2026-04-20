"""
测试用例: 长按会话预览
探索来源: AI自主探索POPO App
用例描述: 在消息列表页长按会话项，验证可进入会话预览模式
"""
import time
from conftest import BaseTest


class TestLongPressSessionPreview(BaseTest):
    """长按会话预览 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_long_press_session_preview(self):
        """
        步骤:
        1. 在消息列表页，对第一个会话项进行长按操作
        2. 验证弹出操作菜单（包含"管理分组"、"全部设为已读"等选项）
        3. 按返回键关闭菜单
        """
        # 对消息列表中第一个会话进行长按（y=300 为第一个会话项区域）
        self.userA.aw.long_press(270, 300, duration=1.5)
        time.sleep(1)

        # 验证弹出了长按操作菜单 - 包含"管理分组"选项
        self.userA.aw.text_exists("管理分组", timeout=5)

        # 按返回键关闭菜单
        self.userA.aw.press_back()
        time.sleep(0.5)

    def teardown(self):
        pass
