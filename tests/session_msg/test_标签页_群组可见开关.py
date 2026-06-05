"""测试用例: 群组会话中标签页单独设置可见开关 | Excel行 28"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestGroupTabSwitch(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_group_tab_visibility_switch(self):
        """操作: 用户在群组会话中设置某个标签页的可见开关 | 预期: 设置成功"""
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)
        self.userA.aw._enter_group_settings_from_chat()
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
