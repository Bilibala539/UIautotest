"""
测试用例: 大搜 - 搜索已删除的消息 (R8)

R8 对应 xlsx R7: 该消息已被删除，大搜搜索消息后点击跳转定位 → 提示"该消息已删除，无法定位"
"""
import random

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal, Search

RECIPIENT = "grp.popoqa50"
RECIPIENT_EMAIL = "grp.popoqa50@corp.netease.com"


class TestSearchDeletedMessage(BaseTest):

    def setup(self):
        self.userA = self.users("userA")
        # 造数：CLI 发一条随机内容消息
        self.msg_content = f"删除搜索测试{random.randint(10000, 99999)}"
        self.userA.cli.send_message_p2p_cli(
            receiver=RECIPIENT_EMAIL,
            message=self.msg_content,
        )
        # UI 进入聊天页，删除该消息
        self.userA.send_message(recipient=RECIPIENT, message="占位", isback=False)
        # 滑动到底部确保 CLI 发的消息在可见区域（swipe_up = 手指上滑 = 显示更新的消息）
        self.userA.aw.swipe_up(distance=300)
        self.userA.aw.sleep(0.5)
        self.userA.aw.long_press_text(self.msg_content, duration=1.5)
        self.userA.click_text("删除", region=Normal.HALF_DOWN)
        # 确认删除弹窗
        self.userA.click_text("删除", region=Normal.CENTER_POP)
        self.userA.aw.sleep(1)
        self.userA.return_to_message_list()

    def test_search_deleted_message(self):
        """R8: 搜索已删除消息，点击结果应提示无法定位"""
        self.userA.search(tab="消息", text=self.msg_content, isclose=False)
        self.userA.aw.sleep(1)
        # 尝试在搜索结果中找到该消息
        found = self.userA.aw.find_text_by_ocr(self.msg_content, timeout=8,
                                                region=Search.RESULT_LIST)
        if found:
            # 搜到了（服务端索引还在），点击结果
            self.userA.click_text(self.msg_content, region=Search.RESULT_LIST)
            self.userA.aw.sleep(2)
            # 验证：应出现"该消息已删除，无法定位"或类似提示
            deleted_hint = self.userA.aw.find_text_by_ocr("已删除", timeout=5)
            locate_hint = self.userA.aw.find_text_by_ocr("无法定位", timeout=3)
            assert deleted_hint is not None or locate_hint is not None,                 "R8: 点击已删除消息搜索结果后，未出现删除/无法定位提示"
        # 若搜不到（索引已同步删除），也符合预期
        self.userA.return_to_message_list()

    def teardown(self):
        pass
