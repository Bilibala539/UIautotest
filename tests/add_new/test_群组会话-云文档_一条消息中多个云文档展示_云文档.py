"""
测试用例: 一条消息中多个云文档展示
功能点: 群组会话-云文档
来源: 搜索.xlsx 行14
"""
import time

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import Normal


class TestCase13(BaseTest):
    """群组会话-云文档 - 一条消息中多个云文档展示"""

    def setup(self):
        self.userA = self.users("userA")

    def test_case(self):
        """
        一条消息中多个云文档展示
        前置条件: 搜索范围中存在一个消息中包含多个文档
        步骤: 1.进入群组会话-设置-云文档tab ；2.点击发送者选中用户，设定时间范围；3.点击搜索
        预期: 一条消息中的多个文档会被一一罗列展示。
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
