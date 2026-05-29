"""
测试用例: 会话盒子关闭的会话入口
覆盖文字用例: 盒子-关闭 (关闭的会话入口验证)
"""
from conftest import BaseTest


class TestSessionBoxClosedSessions(BaseTest):
    """验证打开关闭的会话页面"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
        self.userA.add_to_session_box(self.group_name)
        self.userA.text_exists("会话盒子", timeout=10)

    def test_open_closed_sessions(self):
        self.userA.open_closed_sessions()
        self.userA.aw.find_text_by_ocr("关闭的会话", timeout=5)

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
