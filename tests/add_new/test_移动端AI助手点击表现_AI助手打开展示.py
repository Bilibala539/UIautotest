"""
测试用例: AI助手打开展示
功能点: 会话AI;移动端AI助手点击表现
来源: 搜索.xlsx 行90
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase37(BaseTest):
    """会话AI;移动端AI助手点击表现 - AI助手打开展示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        AI助手打开展示
        前置条件: 
        步骤: 点击右上角的AI助手按钮，查看表现
        预期: 在当前会话内唤起半屏，覆盖消息展示
        """
        # 进入聊天页面
        self.userA.send_message(recipient="grp.popoqa50", message="AI测试", isback=False)
        time.sleep(1)
        # 打开AI助手
        self.userA.aw.click_text("AI", timeout=5, region=Normal.HALF_UP)
        time.sleep(2)
        # 验证AI助手展示
        result = self.userA.aw.find_text_by_ocr("总结", timeout=5)
        assert result is not None, "AI助手应展示功能项"

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=6)
