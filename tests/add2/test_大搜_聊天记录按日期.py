"""测试用例: 大搜 - 聊天记录按日期查看 (R30) [skip]"""
import pytest
from conftest import BaseTest


class TestChatHistoryByDate(BaseTest):
    def setup(self): self.userA = self.users("userA")

    @pytest.mark.skip(reason="R30: 路径待 explorer 探索，图片视频面板内部布局未探")
    def test_chat_history_by_date(self):
        """R30: 聊天记录按日期查看"""
        pass

    def teardown(self): pass
