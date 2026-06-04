"""
测试用例: 标签页优化（3期）- 展示区域标签页自动显示与隐藏
Excel来源: 会话区及消息.xlsx 行 30(云文档tab), 31(链接tab), 32(pin tab), 33(文件tab)
"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestTabAutoShowHide(BaseTest):
    """标签页自动显示与隐藏功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.aw._ensure_message_page()

    def _enter_chat_and_send(self, text):
        """进入聊天页发送消息"""
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_image("CHAT_INPUT_BOX", region="HALF_DOWN")
        self.userA.aw.input_text(text)
        self.userA.aw.click_image("CHAT_SEND_BUTTON", region="HALF_DOWN")
        time.sleep(2)

    def _go_to_tabs(self):
        """从聊天页进入群设置-标签页"""
        self.userA.aw._enter_group_settings_from_chat()
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

    def test_cloud_doc_tab_auto_show(self):
        """
        测试场景: 发送云文档消息后云文档tab自动显示
        预期: 云文档标签页tab自动显示在展示区域
        Excel行号: 30
        """
        self._enter_chat_and_send("https://docs.popo.netease.com/lingxi/test_auto_tab")
        self._go_to_tabs()
        self.userA.aw.text_exists("云文档", timeout=5)

    def test_link_tab_auto_show(self):
        """
        测试场景: 发送链接消息后链接tab自动显示
        预期: 链接标签页tab自动显示在展示区域
        Excel行号: 31
        """
        self._enter_chat_and_send("https://www.163.com")
        self._go_to_tabs()
        self.userA.aw.text_exists("链接", timeout=5)

    def test_pin_tab_auto_show(self):
        """
        测试场景: 对消息进行pin操作后pin tab自动显示
        预期: pin标签页tab自动显示在展示区域
        Excel行号: 32
        """
        self._enter_chat_and_send("pin_tab_auto_test")
        self.userA.aw.pin_message("pin_tab_auto_test")
        time.sleep(1)
        self._go_to_tabs()
        self.userA.aw.text_exists("Pin", timeout=5)

    def test_file_tab_auto_show(self):
        """
        测试场景: 发送文件消息后文件tab自动显示
        预期: 文件标签页tab自动显示在展示区域
        Excel行号: 33
        """
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_image("CHAT_PLUS_BUTTON", region="HALF_DOWN")
        time.sleep(1)
        self.userA.aw.click_text("文件", timeout=5, dy=10)
        time.sleep(2)
        self.userA.aw.click_text("发送", timeout=10)
        time.sleep(2)
        self._go_to_tabs()
        self.userA.aw.text_exists("文件", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list()
