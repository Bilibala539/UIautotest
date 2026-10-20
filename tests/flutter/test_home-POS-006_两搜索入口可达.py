# CASE-ID: home-POS-006
"""Swan 回归·首页：两搜索入口均可达搜索输入页(home-POS-006,部分转换)。

步骤→AW 映射（B 级：音乐 Tab 入口位置受构建漂移影响，需执行轮标定）：
- 音乐 Tab 搜索入口 → go_top_tab('音乐') + open_search_input_page(
  bar_image=SWAN_HOME_MUSIC_SEARCH_BAR, ocr_fallback='跨平台搜索音乐')
- 返回首页 → press_back + assert_on_home
- 推荐页搜索入口 → go_top_tab('推荐') + open_search_input_page(同参)
- 两路均断言落搜索输入页（mixin 尾部断言 hint '搜索歌曲或艺术家等'）

⚠️ 漂移注记：YAML 基于 b34 旧构建（音乐 Tab=搜索卡），swan.py verify R2
拍板新构建"音乐 Tab 已改歌单流、搜索条回归推荐 Tab"。本用例按 YAML 双入口
转换：音乐 Tab 半程若构建确已漂移，会在入口探测处失败——失败即漂移证据，
执行轮按真机现状改参或降级。
cleanup：无（结束态为搜索输入页，随冷启动复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestTwoSearchEntriesReachable(SwanRP03Mixin, BaseTest):
    """音乐 Tab 与推荐页两个搜索入口均能进入搜索输入页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_two_search_entries_reachable(self):
        """音乐 Tab 搜索入口、推荐页搜索入口各进一次搜索输入页。"""
        self.userA.ensure_logged_in_on_home()

        # 入口一：音乐 Tab 搜索卡（YAML 口径；漂移时此处失败即证据）
        self.userA.go_top_tab('音乐')
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        self.userA.press_back()
        self.userA.assert_on_home()

        # 入口二：推荐页搜索入口
        self.userA.go_top_tab('推荐')
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：停在搜索输入页（随冷启动复位）
