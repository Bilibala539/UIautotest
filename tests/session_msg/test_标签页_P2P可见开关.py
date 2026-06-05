"""测试用例: P2P会话中标签页单独设置可见开关 | Excel行 27"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestP2PTabSwitch(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_p2p_tab_visibility_switch(self):
        """操作: 用户在P2P会话中设置某个标签页的可见开关 | 预期: 设置成功"""
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
