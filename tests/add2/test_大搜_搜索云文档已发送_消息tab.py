"""
测试用例: 大搜 - 搜索云文档（已发送过）消息tab (R14-b)
R14: 云空间创建的文档，在会话区发送过 → 消息页签也能搜到
"""
import time
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search
from utils.aw.popo_cli import _run


class TestSearchCloudDocSentInMsgTab(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        self.doc_id = None
        self.doc_title = "autotest_R14_已发送文档"
        data = _run(["doc_create_doc", "docType=2", f"title={self.doc_title}"])
        self.doc_id = data.get("docId")
        doc_url = data.get("url", "")
        self.userA.cli.send_message_p2p_cli(
            receiver="grp.popoqa50@corp.netease.com",
            message=doc_url,
        )
        time.sleep(5)

    def test_cloud_doc_sent_found_in_message_tab(self):
        """R14: 已发送的云文档在消息tab也能搜到"""
        self.userA.search(tab="消息", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        found = self.userA.aw.find_text_by_ocr(self.doc_title, timeout=8,
                                                region=Search.RESULT_LIST)
        assert found is not None, f"消息tab应能搜到已发送的云文档'{self.doc_title}'"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        if self.doc_id:
            try:
                _run(["doc_delete_doc", f"docId={self.doc_id}"])
            except Exception:
                pass
