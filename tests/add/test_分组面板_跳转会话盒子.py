"""
测试用例: 分组面板跳转会话盒子
覆盖文字用例: 跳转会话盒子详情页
"""
from conftest import BaseTest


class TestSessionGroupPanelJumpToSessionBox(BaseTest):
    """验证从分组面板跳转到会话盒子详情页"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
        self.userA.add_to_session_box(self.group_name)
        self.userA.text_exists("会话盒子", timeout=10)

    def test_jump_to_session_box(self):
        self.userA.open_session_box()
        self.userA.aw.find_text_by_ocr("会话盒子", timeout=5)

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
