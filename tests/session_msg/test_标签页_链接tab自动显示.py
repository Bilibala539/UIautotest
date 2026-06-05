"""测试用例: 发送链接消息后链接tab自动显示 | Excel行 31"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestLinkTabAutoShow(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_link_tab_auto_show(self):
        """操作: 在任意会话中发送一条链接消息 | 预期: 链接标签页tab自动显示"""
        self.userA.send_message(recipient=RECIPIENT, message="https://www.163.com")
        self.userA.aw._ensure_message_page()
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("链接", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
