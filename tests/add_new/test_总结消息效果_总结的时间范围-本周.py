"""
测试用例: 总结的时间范围-本周
功能点: 会话AI;总结消息;总结消息效果
来源: 搜索.xlsx 行105
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase49(BaseTest):
    """会话AI;总结消息;总结消息效果 - 总结的时间范围-本周"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        总结的时间范围-本周
        前置条件: 
        步骤: 修改总结的时间范围为本周，查看总结的时间范围是否符合预期
        预期: 总结的范围为当周周一~今天的消息
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手并点击总结消息
        self.userA.aw.click_text("AI", timeout=5, region=(0, 35, 540, 115))
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
