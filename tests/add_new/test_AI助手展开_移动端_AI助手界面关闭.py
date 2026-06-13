"""
测试用例: AI助手界面关闭
功能点: 会话AI;AI助手展开（移动端）
来源: 搜索.xlsx 行93
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase39(BaseTest):
    """会话AI;AI助手展开（移动端） - AI助手界面关闭"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        AI助手界面关闭
        前置条件: 
        步骤: 点击AI助手关闭后，查看界面显示
        预期: AI助手半屏关闭，界面没有明显抖动
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手
        self.userA.aw.click_text("AI", timeout=5, region=Normal.HALF_UP)
        time.sleep(2)
        # 关闭AI助手
        self.userA.aw.press_back()
        time.sleep(1)
        # 验证恢复聊天页面
        self.userA.aw.image_exists(CHAT_PLUS_BUTTON, timeout=5, region=Normal.HALF_DOWN)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
