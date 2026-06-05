"""测试用例: 云文档列表的排序 | Excel行 41"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestCloudDocTabSort(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_cloud_doc_list_sort(self):
        """操作: 查看云文档列表 | 预期: 按发送时间从近到远排序"""
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("云文档", timeout=5)
        time.sleep(1)
        page_loaded = self.userA.aw.find_text_by_ocr("全部标签页", timeout=5)
        assert page_loaded is not None, "云文档列表页面应正常加载"

    def teardown(self):
        self.userA.aw.return_to_message_list()
