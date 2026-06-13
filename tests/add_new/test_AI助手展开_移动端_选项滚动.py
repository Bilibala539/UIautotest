"""
测试用例: 选项滚动
功能点: 会话AI;AI助手展开（移动端）
来源: 搜索.xlsx 行94
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase40(BaseTest):
    """会话AI;AI助手展开（移动端） - 选项滚动"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        选项滚动
        前置条件: 
        步骤: 打开AI助手界面，滑动AI助手中的功能项(补充图片1)
        预期: AI助手的功能允许滚动
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手
        self.userA.aw.click_text("AI", timeout=5, region=Normal.HALF_UP)
        time.sleep(2)
        # 滑动功能列表
        self.userA.aw.swipe_up(distance=200)
        time.sleep(1)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
