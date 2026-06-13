"""
测试用例: 关键词搜索存在结果
功能点: 群组会话-云文档
来源: 搜索.xlsx 行9
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase8(BaseTest):
    """群组会话-云文档 - 关键词搜索存在结果"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        关键词搜索存在结果
        前置条件: 
        步骤: 1.进入群组会话-设置-搜索消息-文件；2.搜索框中输入关键词；3.点击搜索
        预期: 展示近一年的包含关键词的所有文件，灰色字体提醒“已加载全部”。
        """
        # 进入群设置-搜索聊天内容
        self.userA.aw._enter_group_settings("测试测试")
        time.sleep(1)
        self.userA.aw.click_text("搜索聊天内容", timeout=5)
        time.sleep(2)
        # 切换到文件Tab
        self.userA.aw.click_text("文件", timeout=5, region=Normal.HALF_UP)
        time.sleep(1)
        # 输入关键词
        self.userA.aw.click_text("搜索", timeout=3)
        time.sleep(0.5)
        self.userA.aw.input_text("测试")
        time.sleep(2)
        # 验证有搜索结果
        result = self.userA.aw.find_text_by_ocr("没有找到", timeout=3)
        assert result is None, "搜索应有结果"

    def teardown(self):
        self.userA.aw.return_to_message_list(max_back=8)
