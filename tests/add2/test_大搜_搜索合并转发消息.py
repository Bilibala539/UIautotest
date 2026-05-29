"""
测试用例: 大搜 - 搜索合并转发消息 (R9) [skip]
R9: 搜索被合并转发的消息
"""
import pytest
from conftest import BaseTest


class TestSearchMergedMessage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    @pytest.mark.skip(reason="R9: merge_forward_message 未在 PPUser 封装，需要 AW 层实现")
    def test_search_merged_forwarded_message(self):
        """R9: 消息合并转发后，全部tab和消息tab均能搜到原始消息和转发消息"""
        pass

    def teardown(self):
        pass
