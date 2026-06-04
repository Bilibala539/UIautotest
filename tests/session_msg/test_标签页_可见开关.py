"""
测试用例: 标签页优化（3期）- 各类型会话标签页可见开关
Excel来源: 会话区及消息.xlsx 行 27(P2P标签页开关), 28(群组标签页开关)
"""
import time
from conftest import BaseTest

RECIPIENT_P2P = "grp.popoqa50"
RECIPIENT_GROUP = "grp.popoqa93"


class TestTabPageVisibilitySwitch(BaseTest):
    """标签页可见开关设置测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.aw._ensure_message_page()

    def test_p2p_tab_visibility_switch(self):
        """
        测试场景: P2P会话中标签页单独设置可见开关
        预期: 该标签页的可见开关设置成功
        Excel行号: 27
        """
        self.userA.aw._enter_p2p_settings(RECIPIENT_P2P)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def test_group_tab_visibility_switch(self):
        """
        测试场景: 群组会话中标签页单独设置可见开关
        预期: 该标签页的可见开关设置成功
        Excel行号: 28
        """
        # 先进入群聊天页，再从聊天页进入群设置
        self.userA.aw._enter_chat_page(RECIPIENT_GROUP)
        time.sleep(1)
        self.userA.aw._enter_group_settings_from_chat()
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
