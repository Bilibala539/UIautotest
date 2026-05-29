"""测试用例: 大搜 - 搜索云文档（已发送过）(R15) [skip]"""
import pytest
from conftest import BaseTest


class TestSearchCloudDocSent(BaseTest):
    def setup(self): self.userA = self.users("userA")

    @pytest.mark.skip(reason="R15: 需确认已发送过的云文档搜索关键词，云空间tab搜索流程待验证")
    def test_search_cloud_doc_sent(self):
        """R15: 云文档已发送过，全部tab和消息tab均能搜到"""
        pass

    def teardown(self): pass
