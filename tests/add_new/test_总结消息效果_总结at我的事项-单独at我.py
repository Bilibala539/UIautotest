"""
测试用例: 总结@我的事项-单独@我
功能点: 会话AI;总结消息;总结消息效果
来源: 搜索.xlsx 行106
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase50(BaseTest):
    """会话AI;总结消息;总结消息效果 - 总结@我的事项-单独@我"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        总结@我的事项-单独@我
        前置条件: 
        步骤: 点击总结消息中@我的技能
        预期: @我技能总结的范围中，包含@我的消息
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手并点击总结消息
        self.userA.aw.click_text("AI", timeout=5, region=Normal.HALF_UP)
        time.sleep(2)
        self.userA.aw.click_text("总结消息", timeout=5)
        time.sleep(2)
        pos = self.userA.aw.find_text_by_ocr("@我的", timeout=5)
        if pos:
            self.userA.aw.tap(pos[0], pos[1])
            time.sleep(1)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
