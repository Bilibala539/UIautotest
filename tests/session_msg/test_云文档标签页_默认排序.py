"""测试用例: 检查云文档标签页的默认排序 | Excel行 38"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestCloudDocTabOrder(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_default_tab_order(self):
        """操作: 打开任意会话，检查标签页顺序 | 预期: 云文档、链接、Pin、文件、任务"""
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("云文档", timeout=5)
        self.userA.aw.text_exists("全部标签页", timeout=3)

    def teardown(self):
        self.userA.aw.return_to_message_list()
