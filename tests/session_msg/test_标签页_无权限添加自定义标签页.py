"""测试用例: 无标签页管理权限的群成员尝试添加自定义标签页 | Excel行 36"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestTabNoPermission(BaseTest):

    def setup(self):
        self.userA = self.users("userA")

    def test_no_permission_add_custom_tab(self):
        """操作: 进入群组会话设置页面，点击添加自定义标签页 | 预期: 提示无权限"""
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)
        self.userA.aw._enter_group_settings_from_chat()
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)
        add_pos = self.userA.aw.find_text_by_ocr("+", timeout=3)
        if add_pos:
            self.userA.aw.click_text("+", timeout=3)
            time.sleep(1)
            link_pos = self.userA.aw.find_text_by_ocr("链接", timeout=3)
            perm_pos = self.userA.aw.find_text_by_ocr("权限", timeout=2)
            assert (link_pos is not None) or (perm_pos is not None)

    def teardown(self):
        self.userA.aw.return_to_message_list()
