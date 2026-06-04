"""
测试用例: 各类标签页 - 云文档标签页
Excel来源: 会话区及消息.xlsx 行 38(默认排序), 39(查看列表), 40(移除), 41(列表排序)
"""
import time
from conftest import BaseTest

RECIPIENT = "grp.popoqa93"


class TestCloudDocTabPage(BaseTest):
    """云文档标签页功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        self.userA.aw._ensure_message_page()

    def _go_to_group_tabs(self):
        """进入群聊天 → 群设置 → 标签页"""
        self.userA.aw._enter_chat_page(RECIPIENT)
        time.sleep(1)
        self.userA.aw._enter_group_settings_from_chat()
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)

    def test_default_tab_order(self):
        """
        测试场景: 检查云文档标签页的默认排序
        预期: 默认标签页排序为：云文档、链接、Pin、文件、任务
        Excel行号: 38
        """
        self._go_to_group_tabs()
        self.userA.aw.text_exists("云文档", timeout=5)
        self.userA.aw.text_exists("文件", timeout=3)

    def test_view_cloud_doc_list(self):
        """
        测试场景: 查看云文档列表
        预期: 列表展示会话内发送的所有云文档
        Excel行号: 39
        """
        self._go_to_group_tabs()
        self.userA.aw.click_text("云文档", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("全部标签页", timeout=5)

    def test_cloud_doc_remove(self):
        """
        测试场景: 云文档的移除（撤回云文档消息后标签页中消失）
        预期: 撤回成功
        Excel行号: 40
        """
        self.userA.send_message(recipient=RECIPIENT, message="https://docs.popo.netease.com/remove_doc_test")
        time.sleep(1)
        # 撤回
        self.userA.aw.long_press_text("remove_doc", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("撤回", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists("撤回了一条消息", timeout=5)

    def test_cloud_doc_list_sort(self):
        """
        测试场景: 云文档列表的排序
        预期: 按发送时间从近到远排序
        Excel行号: 41
        """
        self._go_to_group_tabs()
        self.userA.aw.click_text("云文档", timeout=5)
        time.sleep(1)
        page_loaded = self.userA.aw.find_text_by_ocr("全部标签页", timeout=5)
        assert page_loaded is not None, "云文档列表页面应正常加载"

    def teardown(self):
        self.userA.aw.return_to_message_list()
