"""
测试用例: 云文档搜索后点击
功能点: 群组会话-云文档
来源: 搜索.xlsx 行15
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase14(BaseTest):
    """群组会话-云文档 - 云文档搜索后点击"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        云文档搜索后点击
        前置条件: 
        步骤: 1.进入群组会话-设置-云文档tab ；2.点击任一云文档
        预期: 浏览器打开这个云文档
        """
        # 进入群设置-搜索聊天内容
        self.userA.aw._enter_group_settings("测试测试")
        time.sleep(1)
        self.userA.aw.click_text("搜索聊天内容", timeout=5)
        time.sleep(2)
        # 切换到云文档Tab
        self.userA.aw.click_text("云文档", timeout=5, region=Normal.HALF_UP)
        time.sleep(1)
        # 验证页面正确加载
        self.userA.aw.text_exists("发送者", timeout=5)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=8)
