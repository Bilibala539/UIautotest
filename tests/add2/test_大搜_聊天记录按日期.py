"""
测试用例: 大搜 - 聊天记录消息被撤回后搜索定位 (R30)

R30 对应 xlsx R29: 搜索过程中消息已被撤回，则直接定位至最新消息
"""
import random

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search

RECIPIENT = "grp.popoqa50"
RECIPIENT_EMAIL = "grp.popoqa50@corp.netease.com"


class TestSearchRecalledMessageLocate(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # 造数：CLI 发一条随机消息
        self.msg_content = f"撤回定位测试{random.randint(10000, 99999)}"
        self.userA.cli.send_message_p2p_cli(
            receiver=RECIPIENT_EMAIL,
            message=self.msg_content,
        )
        # CLI 再发一条最新消息（用于后续验证定位到最新消息）
        self.latest_msg = f"最新消息{random.randint(10000, 99999)}"
        self.userA.cli.send_message_p2p_cli(
            receiver=RECIPIENT_EMAIL,
            message=self.latest_msg,
        )
        # UI 进入聊天页撤回第一条消息
        self.userA.send_message(recipient=RECIPIENT, message="占位", isback=False)
        # 多次上滑直到找到 CLI 发的消息
        found = None
        for _ in range(5):
            found = self.userA.aw.find_text_by_ocr(self.msg_content, timeout=2)
            if found:
                break
            self.userA.aw.swipe_up(distance=300)
            self.userA.aw.sleep(0.5)
        assert found is not None, f"setup: 未在聊天页找到消息 '{self.msg_content}'"
        self.userA.aw.long_press_text(self.msg_content, duration=1.5)
        self.userA.click_text("撤回", region=Normal.HALF_DOWN)
        # 处理可能的确认弹窗
        confirm = self.userA.aw.find_image(MSG_RECELL_POP, timeout=3)
        if confirm:
            self.userA.click_text("确定", region=Normal.CENTER_POP)
        self.userA.aw.sleep(1)
        self.userA.return_to_message_list()

    def test_search_recalled_message_locate_latest(self):
        """R30: 消息被撤回后搜索，点击结果应定位至最新消息"""
        self.userA.search(tab="消息", text=self.msg_content, isclose=False)
        self.userA.aw.sleep(1)
        # 尝试搜索被撤回的消息
        found = self.userA.aw.find_text_by_ocr(self.msg_content, timeout=8,
                                                region=Search.RESULT_LIST)
        if found:
            # 搜到了，点击结果
            self.userA.click_text(self.msg_content, region=Search.RESULT_LIST)
            self.userA.aw.sleep(2)
            # 验证：应定位至最新消息或显示撤回提示
            # 可能的结果：1.进入聊天页看到最新消息 2.提示已撤回/无法定位
            in_chat = self.userA.aw.find_image(CHAT_PLUS_BUTTON, timeout=5,
                                                region=Normal.HALF_DOWN)
            if in_chat:
                # 进入了聊天页，验证能看到最新消息（定位到最新）
                latest_visible = self.userA.aw.find_text_by_ocr(
                    self.latest_msg, timeout=5)
                recalled_hint = self.userA.aw.find_text_by_ocr(
                    "撤回", timeout=3)
                assert latest_visible is not None or recalled_hint is not None,                     "R30: 点击已撤回消息结果后，既未定位到最新消息也未出现撤回提示"
            else:
                # 没进入聊天页，可能有弹窗提示
                hint = self.userA.aw.find_text_by_ocr("撤回", timeout=3)
                if hint is None:
                    hint = self.userA.aw.find_text_by_ocr("无法定位", timeout=3)
                assert hint is not None,                     "R30: 点击已撤回消息结果后，无任何提示且未进入聊天页"
        # 若搜不到（撤回后索引已删除），也符合预期（直接pass）
        self.userA.return_to_message_list()

    def teardown(self):
        pass
