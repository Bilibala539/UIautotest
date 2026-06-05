"""测试用例: 发送云文档消息后云文档tab自动显示 | Excel行 30"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestCloudDocTabAutoShow(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_cloud_doc_tab_auto_show(self):
        """操作: 在任意会话中发送一条云文档消息 | 预期: 云文档标签页tab自动显示"""
        self.userA.send_message(recipient=RECIPIENT, message="https://docs.popo.netease.com/lingxi/auto_tab")
        self.userA.aw._ensure_message_page()
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("云文档", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
