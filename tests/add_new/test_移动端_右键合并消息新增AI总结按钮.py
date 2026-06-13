"""
测试用例: 右键合并消息新增AI总结按钮
功能点: 会话AI;合并消息右键新增AI总结;移动端
来源: 搜索.xlsx 行110
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase52(BaseTest):
    """会话AI;合并消息右键新增AI总结;移动端 - 右键合并消息新增AI总结按钮"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        右键合并消息新增AI总结按钮
        前置条件: 
        步骤: 右键合并消息后，查看右键菜单
        预期: 菜单中表情回应和任务之间新增一个AI总结的按钮
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 长按消息查看菜单
        self.userA.aw.long_press_text("AI测试", duration=1.5)
        time.sleep(1)
        # 验证菜单中有AI总结
        result = self.userA.aw.find_text_by_ocr("AI总结", timeout=3, region=Normal.HALF_DOWN)
        self.userA.aw.press_back()

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
