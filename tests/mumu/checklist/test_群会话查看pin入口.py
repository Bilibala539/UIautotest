"""
测试用例: 群会话查看Pin入口
探索来源: AI自主探索POPO App生成
探索补全: 原始用例步骤模糊，通过自主探索App补全操作路径
实际流程: 进入群聊→发送消息→长按消息→验证菜单中有Pin选项
"""
from conftest import BaseTest
import time


class TestGroupChatPinEntry(BaseTest):
    """群会话查看Pin入口 测试类"""

    def setup(self):
        self.userA = self.users("userA")

    def test_group_chat_has_pin_entry(self):
        """
        在群聊中发送消息，长按消息验证弹出菜单中有Pin选项
        """
        # 发送一条消息到群聊（使用已有AW方法，isback=False保持在聊天页面）
        msg = self.userA.aw.random_digits(8)
        self.userA.send_message("grp.popoqa50@corp.netease.com", msg, isback=False)
        time.sleep(1)

        # 长按消息，弹出操作菜单
        self.userA.aw.long_press_text(msg, duration=1.5)
        time.sleep(1)

        # 验证菜单中有Pin选项
        pin_pos = self.userA.aw.find_text_by_ocr("Pin", timeout=5)
        assert pin_pos is not None, "长按消息菜单中应有Pin选项"

        # 关闭菜单
        self.userA.aw.press_back()
        time.sleep(0.5)

    def teardown(self):
        pass
