"""测试用例: 云文档的移除（撤回消息后从列表消失）| Excel行 40"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestCloudDocRemove(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_cloud_doc_remove(self):
        """操作: 撤回或删除服务端的云文档消息 | 预期: 云文档标签页中移除该云文档"""
        msg = "撤回测试"
        self.userA.send_message(recipient=RECIPIENT, message=msg)
        time.sleep(1)
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)
        self.userA.aw.press_back()
        time.sleep(0.5)
        self.userA.aw.long_press_text(msg, timeout=10, duration=1.5)
        time.sleep(1)
        self.userA.aw.click_text("撤回", timeout=5)
        time.sleep(1)
        confirm = self.userA.aw.find_text_by_ocr("确定", timeout=3)
        if confirm:
            self.userA.aw.click_text("确定")
            time.sleep(1)
        self.userA.aw.text_exists("撤回了一条消息", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
