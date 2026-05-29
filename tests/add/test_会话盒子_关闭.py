"""
测试用例: 会话盒子-关闭
功能点: 关闭会话盒子
操作步骤:
  1. (setup) 通过设置页将一个会话添加到盒子
  2. 长按消息列表中的"会话盒子"条目 → 点击"关闭"
预期结果: "会话盒子"条目从消息列表消失
"""
from image.image_name_mapping import SESSION_BOX
from conftest import BaseTest


class TestCloseSessionBox(BaseTest):
    """会话盒子-关闭"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
        self.userA.add_to_session_box(self.group_name)
        self.userA.text_exists("会话盒子", timeout=10)

    def test_close_session_box(self):
        self.userA.close_conversation_box("会话盒子")
        pos = self.userA.aw.find_image(SESSION_BOX, timeout=5)
        assert pos is None, "会话盒子条目应已从消息列表消失"

    def teardown(self):
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
