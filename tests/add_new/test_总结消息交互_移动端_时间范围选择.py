"""
测试用例: 时间范围选择
功能点: 会话AI;总结消息;总结消息交互（移动端）
来源: 搜索.xlsx 行98
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase43(BaseTest):
    """会话AI;总结消息;总结消息交互（移动端） - 时间范围选择"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        时间范围选择
        前置条件: 
        步骤: 点击总结消息后，选择时间范围
        预期: 点击切换后时间后，按钮显示为对应的事件范围，发送后总结切换后的事件的消息
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手并点击总结消息
        self.userA.aw.click_text("AI", timeout=5, region=Normal.HALF_UP)
        time.sleep(2)
        self.userA.aw.click_text("总结消息", timeout=5)
        time.sleep(2)
        # 选择时间范围
        pos = self.userA.aw.find_text_by_ocr("本周", timeout=5)
        if pos:
            self.userA.aw.tap(pos[0], pos[1])
            time.sleep(1)
            self.userA.aw.text_exists("本周", timeout=3)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
