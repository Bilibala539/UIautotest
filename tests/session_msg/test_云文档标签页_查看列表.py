"""测试用例: 查看云文档列表 | Excel行 39"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestCloudDocTabList(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_view_cloud_doc_list(self):
        """操作: 点击云文档标签页 | 预期: 列表展示会话内发送的所有云文档"""
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("云文档", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
