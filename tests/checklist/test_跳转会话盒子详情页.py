"""
测试用例: 跳转会话盒子详情页
功能点: 新增会话分组模块
操作步骤: 分组栏展开后，点击会话盒子
预期结果: 跳转到会话盒子列表页
"""
from conftest import BaseTest


class TestOpenSessionBoxDetail(BaseTest):
    """跳转会话盒子详情页"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
        self.userA.add_to_session_box(self.group_name)
        self.userA.text_exists("会话盒子", timeout=10)

    def test_open_session_box_detail(self):
        self.userA.open_session_group_panel()
        self.userA.open_session_box()

    def teardown(self):
        self.userA.aw.press_back()
        try:
            if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
                self.userA.remove_from_session_box(self.group_name)
        except Exception:
            pass
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
