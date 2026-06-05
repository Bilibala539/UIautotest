"""
测试用例: 大搜 - 搜索云文档（未发送过）消息tab (R13-b)
R13: 云空间创建的文档，没有在会话区发送过 → 消息页签搜不到
"""
import time
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search
from utils.aw.popo_cli import _run


class TestSearchCloudDocUnsentNotInMsgTab(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        self.doc_id = None
        self.doc_title = "autotest_R13_未发送文档"
        data = _run(["doc_create_doc", "docType=2", f"title={self.doc_title}"])
        self.doc_id = data.get("docId")
        time.sleep(3)

    def test_cloud_doc_unsent_not_found_in_message_tab(self):
        """R13: 未发送的云文档在消息tab搜不到"""
        self.userA.search(tab="消息", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        self.userA.text_not_exists(self.doc_title, region=Search.RESULT_LIST, timeout=5)
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        if self.doc_id:
            try:
                _run(["doc_delete_doc", f"docId={self.doc_id}"])
            except Exception:
                pass
