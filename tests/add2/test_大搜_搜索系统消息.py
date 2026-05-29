"""
测试用例: 大搜 - 搜索系统消息 (R8) [skip]
R8: 搜索已删除的系统消息
"""
import pytest
from conftest import BaseTest


class TestSearchSystemMessage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.skip(reason="R8: 路径待 explorer 探索，系统消息搜索入口未确认")
    def test_search_system_message(self):
        """R8: 搜索系统消息"""
        pass

    def teardown(self):
        pass
