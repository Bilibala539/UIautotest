"""测试用例: 大搜 - 聊天记录按文件查看 (R31) [skip]"""
import pytest
from conftest import BaseTest


class TestChatHistoryByFile(BaseTest):
    def setup(self): self.userA = self.users("userA")

    @pytest.mark.skip(reason="R31: 路径待 explorer 探索，聊天记录文件标签内部布局未探")
    def test_chat_history_by_file(self):
        """R31: 聊天记录按文件查看"""
        pass

    def teardown(self): pass
