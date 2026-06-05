"""测试用例: 对消息进行pin操作后pin tab自动显示 | Excel行 32"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestPinTabAutoShow(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_pin_tab_auto_show(self):
        """操作: 在任意会话中对一条消息进行pin操作 | 预期: pin标签页tab自动显示"""
        self.userA.send_message(recipient=RECIPIENT, message="pintabtest123", isback=False)
        time.sleep(0.5)
        self.userA.aw.pin_message("pintabtest123")
        time.sleep(1)
        self.userA.aw._ensure_message_page()
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("Pin", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
