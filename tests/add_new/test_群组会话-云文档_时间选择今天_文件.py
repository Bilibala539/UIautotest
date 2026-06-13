"""
测试用例: 时间选择今天
功能点: 群组会话-云文档
来源: 搜索.xlsx 行5
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase4(BaseTest):
    """群组会话-云文档 - 时间选择今天"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        时间选择今天
        前置条件: 群组存在今日文件
        步骤: 1.进入群组会话-设置-文件；2.下拉选择时间选择今天；3.点击搜索
        预期: 展示今天之内所有的文件
        """
        # 进入群设置-搜索聊天内容
        self.userA.aw._enter_group_settings("测试测试")
        time.sleep(1)
        self.userA.aw.click_text("搜索聊天内容", timeout=5)
        time.sleep(2)
        # 切换到文件Tab
        self.userA.aw.click_text("文件", timeout=5, region=Normal.HALF_UP)
        time.sleep(1)
        # 选择时间-今天
        self.userA.aw.click_text("全部时间", timeout=5)
        time.sleep(1)
        self.userA.aw.click_text("今天", timeout=5)
        time.sleep(2)
        # 验证时间筛选生效
        self.userA.aw.text_exists("今天", timeout=5, region=Normal.HALF_UP)

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=8)
