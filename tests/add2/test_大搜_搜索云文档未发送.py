"""测试用例: 大搜 - 搜索云文档（未发送过）(R14) [skip]"""
import pytest
from conftest import BaseTest


class TestSearchCloudDocUnsent(BaseTest):
    def setup(self): self.userA = self.users("userA")

    @pytest.mark.skip(reason="R14: 需确认未发送过的云文档搜索关键词，云空间tab搜索流程待验证")
    def test_search_cloud_doc_unsent(self):
        """R14: 云文档未发送过，全部tab能搜到，消息tab搜不到"""
        pass

    def teardown(self): pass
