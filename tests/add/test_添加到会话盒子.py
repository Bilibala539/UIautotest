"""
测试用例: 添加会话到会话盒子
探索补全: 从聊天设置页面点击"添加到会话盒子"
"""
from conftest import BaseTest


class TestAddToSessionBox(BaseTest):
    """添加会话到会话盒子测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")

    def test_add_to_session_box(self):
        self.userA.add_to_session_box(self.group_name)
        self.userA.text_exists("会话盒子", timeout=10)

    def teardown(self):
        try:
            if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
                self.userA.remove_from_session_box(self.group_name)
        except Exception:
            pass
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
