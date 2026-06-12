"""
测试用例: 会话盒子打开
覆盖文字用例: 盒子相关操作前置
"""
from conftest import BaseTest


class TestSessionBoxOpen(BaseTest):
    """验证打开会话盒子页面"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group(desired_name="会话盒子测试群")
        # 清理残留状态
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
        self.userA.add_to_session_box(self.group_name)

    def test_open_session_box(self):
        self.userA.open_session_box()
        self.userA.text_exists("会话盒子", timeout=5)

    def teardown(self):
        try:
            self.userA.remove_from_session_box(self.group_name)
        except Exception:
            pass
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
