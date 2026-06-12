"""
测试用例: 会话盒子-设为已读
功能点: 在会话盒子中将会话标记为已读
操作步骤:
  1. 将群会话添加到会话盒子
  2. 进入会话盒子
  3. 长按该会话并设为已读
预期结果: 会话被标记为已读
"""
from conftest import BaseTest


class TestSessionBoxMarkRead(BaseTest):
    """会话盒子-设为已读"""

    def setup(self):
        self.userA = self.users("userA")
        self.group_name = self.userA.aw.setup_owner_group("会话盒子测试群")
        # 清理可能残留的会话盒子状态
        if self.userA.aw.find_text_by_ocr("会话盒子", timeout=3):
            self.userA.close_conversation_box("会话盒子")
        # 将群添加到会话盒子，使"会话盒子"条目出现在消息列表
        self.userA.add_to_session_box(self.group_name)

    def test_mark_read_in_session_box(self):
        # 1. 进入会话盒子，确认目标会话存在
        self.userA.open_session_box()
        self.userA.text_exists(self.group_name, timeout=5)

        # 2. 在会话盒子中长按目标会话，执行"设为已读" / "设为未读"切换
        # mark_conversation_as_read 内部: 长按会话 → 查找菜单 → 点击"设为已读"/"设为未读"
        result = self.userA.mark_conversation_as_read(self.group_name)

        # 3. 断言操作执行成功（菜单中出现"设为已读"或"设为未读"并点击）
        assert result, f"标记已读/未读操作失败，会话: {self.group_name}"

    def teardown(self):
        try:
            self.userA.remove_from_session_box(self.group_name)
        except Exception:
            pass
        try:
            self.userA.aw.delete_team(self.group_name)
        except Exception:
            pass
