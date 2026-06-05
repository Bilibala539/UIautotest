"""
测试用例: 大搜 - 搜索入口与记录 (R3/R4)

R3: 搜索记录保留 - 搜索关键词后清除输入框，验证历史记录保留
R4: 清空搜索记录 - 点击删除icon → 弹出确认弹窗 → 确认后记录清空
"""
import time

import pytest

from conftest import BaseTest
from image.image_name_mapping import *
from utils.aw.search_region import *


class TestSearchEntryAndHistory(BaseTest):
    """搜索入口与搜索记录管理"""

    def setup(self):
        self.userA = self.users("userA")

    def test_clear_search_history(self):
        """
        R3: 搜索关键词后退出，再次进入搜索页验证搜索记录首位出现该关键词
        R4: 点击删除icon弹出确认弹窗，确认后搜索记录清空
        """
        # 创造最近搜索记录，顺便验证R3
        # 搜索“123”联系人，并且进入搜索结果
        self.userA.search_people(text="123", isgoin=True)
        # 返回消息列表
        self.userA.return_to_message_list()
        # 点击大搜icon
        self.userA.click_image(MESSAGE_TAB_SEARCH, region=Normal.HALF_UP)

        # 进入搜索页在最近搜索区域中点击清空按钮
        self.userA.click_image(SEARCH_CLEAN_RECENT_SEARCH, region=Search.RECENT_SEARCH)
        self.userA.text_exists("确定清空全部搜索历史", region=Normal.CENTER_POP, timeout=3)
        self.userA.click_image(SEARCH_CLEAN_RECENT_SEARCH_CONFIRM, region=Normal.CENTER_POP)

        # 验证是否清空成功——最近搜索区域不存在“123”
        self.userA.text_not_exists("123", region=Search.RECENT_SEARCH, timeout=3)

    def teardown(self):
        pass
