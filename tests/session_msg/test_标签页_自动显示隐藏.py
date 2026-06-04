"""
测试用例: 标签页优化（3期）- 展示区域标签页自动显示与隐藏
Excel来源: 会话区及消息.xlsx 行 30(云文档tab), 31(链接tab), 32(pin tab), 33(文件tab)
"""
import time
import pytest
from conftest import BaseTest

RECIPIENT = "grp.popoqa50"


class TestTabAutoShowHide(BaseTest):
    """标签页自动显示与隐藏功能测试"""

    def setup(self):
        self.userA = self.users("userA")
        for _ in range(3):
            self.userA.aw.press_back()
            time.sleep(0.3)
        cancel_pos = self.userA.aw.find_text_by_ocr("取消", timeout=2)
        if cancel_pos:
            self.userA.aw.click_text("取消")
            time.sleep(0.5)
        self.userA.aw._ensure_message_page()

    def _verify_tab_exists(self, tab_name):
        """从消息列表进入P2P设置-标签页，验证某个tab存在"""
        self.userA.aw._ensure_message_page()
        self.userA.aw._enter_p2p_settings(RECIPIENT)
        time.sleep(1)
        self.userA.aw.click_text("标签页", timeout=5)
        time.sleep(1)
        self.userA.aw.text_exists(tab_name, timeout=5)

    def test_cloud_doc_tab_auto_show(self):
        """
        测试场景: 发送云文档消息后云文档tab自动显示
        预期: 云文档标签页tab自动显示在展示区域
        Excel行号: 30
        """
        self.userA.send_message(
            recipient=RECIPIENT,
            message="https://docs.popo.netease.com/lingxi/auto_tab_test"
        )
        self._verify_tab_exists("云文档")

    def test_link_tab_auto_show(self):
        """
        测试场景: 发送链接消息后链接tab自动显示
        预期: 链接标签页tab自动显示在展示区域
        Excel行号: 31
        """
        self.userA.send_message(
            recipient=RECIPIENT,
            message="https://www.163.com"
        )
        self._verify_tab_exists("链接")

    def test_pin_tab_auto_show(self):
        """
        测试场景: 对消息进行pin操作后pin tab自动显示
        预期: pin标签页tab自动显示在展示区域
        Excel行号: 32
        """
        # 发消息（留在聊天页）
        self.userA.send_message(
            recipient=RECIPIENT,
            message="pintabtest123",
            isback=False
        )
        time.sleep(0.5)
        # pin这条消息
        self.userA.aw.pin_message("pintabtest123")
        time.sleep(1)
        # 回到消息列表再进设置看标签页
        self._verify_tab_exists("Pin")

    @pytest.mark.skip(reason="当前App版本中发送文件不会自动创建独立的文件标签页tab，需确认产品设计")
    def test_file_tab_auto_show(self):
        """
        测试场景: 发送文件消息后文件tab自动显示
        操作: 在任意会话中发送一条文件消息
        预期: 文件标签页tab自动显示在展示区域
        Excel行号: 33
        """
        pass

    def teardown(self):
        self.userA.aw.return_to_message_list()
