"""
测试用例: 大搜 - 搜索云文档（未发送过）云空间tab (R13-a)
R13: 云空间创建的文档，没有在会话区发送过 → 全部/文档页签能搜到
"""
import time
from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search
from utils.aw.popo_cli import _run


class TestSearchCloudDocUnsentInCloudTab(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        self.doc_id = None
        self.doc_title = "autotest_R13_未发送文档"
        # CLI 造数：创建云文档（不发送到会话），用 _run 统一处理返回值
        data = _run(["doc_create_doc", "docType=2", f"title={self.doc_title}"])
        self.doc_id = data.get("docId")
        time.sleep(3)  # 等待索引生效

    def test_cloud_doc_unsent_found_in_cloud_tab(self):
        """R13: 未发送的云文档在云空间tab能搜到"""
        self.userA.search(tab="云空间", text=self.doc_title, isclose=False)
        self.userA.aw.sleep(3)
        found = self.userA.aw.find_text_by_ocr(self.doc_title, timeout=8,
                                                region=Search.RESULT_LIST)
        assert found is not None, f"云空间tab应能搜到未发送的云文档'{self.doc_title}'"
        self.userA.click_image(SEARCH_CANCEL, region=Normal.HALF_UP)

    def teardown(self):
        if self.doc_id:
            try:
                _run(["doc_delete_doc", f"docId={self.doc_id}"])
            except Exception:
                pass
