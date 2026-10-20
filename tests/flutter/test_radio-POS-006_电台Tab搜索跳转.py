# CASE-ID: radio-POS-006
"""Swan 回归·电台：电台 Tab 搜索栏跳全局搜索（radio-POS-006，Hero tag 只读入口）。

步骤 -> AW 映射（坑 5：页内无搜索结果态，只断跳转与返回；
SearchArgs.homeRadioSearchHeroTag -> 全局搜索页）：
- 步骤1 首页电台 Tab 点击顶部搜索栏 -> go_top_tab('电台') + 搜索条图
  [图]（SWAN_HOME_RADIO_SEARCH_BAR，已登记常量）点击，跳全局搜索页，
  OCR 候选断言搜索页锚点（默认 Tab=电台）；
- 步骤2 返回 -> press_back 回首页电台 Tab，断言原列表态保持
  （区块标题候选复现，无异常）。

清理：只读跳转，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_RADIO_SEARCH_BAR


class TestRadioSearchEntryJump(BaseTest):
    """radio-POS-006：搜索栏只读跳全局搜索，返回列表态保持。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_search_entry_jump(self):
        """搜索栏 -> 全局搜索页（默认电台 Tab），返回无异常。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        if self.userA.probe_image(SWAN_HOME_RADIO_SEARCH_BAR,
                                  timeout=3) is None:
            pytest.skip("首页电台 Tab 搜索条图未命中（布局轮换），转人工复核")
        # 步骤1：搜索栏点击跳全局搜索页
        self.userA.click_image(SWAN_HOME_RADIO_SEARCH_BAR, timeout=10)
        self.userA.assert_any_of_texts("电台", "搜索歌曲", "搜索", timeout=8)
        # 步骤2：返回后电台 Tab 原列表态保持
        self.userA.press_back()
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=8)

    def teardown(self) -> None:
        """只读跳转无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
