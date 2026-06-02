"""
测试用例: 大搜 - 搜索已撤回消息 (R8)

R8: CLI发消息 → UI撤回消息 → 大搜搜索该消息 → 验证点击结果无法定位（消息已撤回）
"""
import random

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search

RECIPIENT = "grp.popoqa50"


class TestSearchSystemMessage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # 造数：发一条带随机内容的消息（CLI），再通过 UI 进入会话撤回
        self.msg_content = f"撤回搜索测试{random.randint(10000, 99999)}"
        # CLI 发消息到 P2P 会话
        self.userA.cli.send_message_p2p_cli(
            receiver="grp.popoqa50@corp.netease.com",
            message=self.msg_content,
        )
        # UI 进入会话，撤回刚发送的消息
        self.userA.aw.send_message(recipient=RECIPIENT, message=None, isback=False)
        self.userA.recall_message(self.msg_content)
        self.userA.return_to_message_list()

    def test_search_recalled_message(self):
        """R8: 搜索已撤回消息，点击结果无法定位原消息位置"""
        self.userA.search(tab="消息", text=self.msg_content, isclose=False)
        self.userA.aw.sleep(1)
        # 两种可能的预期结果：
        # 1. 搜不到（撤回消息从索引中删除）
        # 2. 能搜到但标注"消息已撤回"
        found = self.userA.aw.find_text_by_ocr(self.msg_content, timeout=5,
                                                region=Search.RESULT_LIST)
        if found:
            # 若搜到，点击后应显示"撤回"相关提示或无法定位
            self.userA.click_text(self.msg_content, region=Search.RESULT_LIST)
            self.userA.aw.sleep(1)
            recalled = self.userA.aw.find_text_by_ocr("撤回", timeout=3)
            assert recalled is not None or \
                   self.userA.aw.find_text_by_ocr("无法定位", timeout=2) is not None, \
                "R8: 点击已撤回消息结果后，未显示撤回提示"
        # 若搜不到也符合预期（撤回消息已从搜索索引移除）
        self.userA.return_to_message_list()

    def teardown(self):
        pass
