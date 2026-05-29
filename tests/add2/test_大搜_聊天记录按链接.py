"""测试用例: 大搜 - 聊天记录按链接查看 (R33) [skip]"""
import pytest
from conftest import BaseTest


class TestChatHistoryByLink(BaseTest):
    def setup(self): self.userA = self.users("userA")

    @pytest.mark.skip(reason="R33: 路径待 explorer 探索，聊天记录链接标签内部布局未探")
    def test_chat_history_by_link(self):
        """R33: 聊天记录按链接查看"""
        pass

    def teardown(self): pass
