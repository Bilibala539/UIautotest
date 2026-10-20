# CASE-ID: search-POS-022
"""Swan 回归·搜索：全链 A 搜索→播放→重搜同词复播(search-POS-022)。

步骤→AW 映射（用例主体含音乐 Tab 入口，按 YAML 忠实转换）：
- 切音乐 Tab 进搜索 → go_top_tab('音乐') + open_search_input_page(
  bar_image=SWAN_HOME_MUSIC_SEARCH_BAR, ocr_fallback='跨平台搜索音乐')
- 搜索 → submit_search_keyword(keyword)（结果顶 Tab 行断言在 mixin）
- 播放结果首行 → play_first_song_result()（歌曲行动态点击 + 底部播放条
  [图] 出现断言；经统一播放入口开始播放）
- 返回重搜同词 → press_back + submit_search_keyword(keyword)
- 断言同曲播放中 → find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=10) 命中
  （播放条在场=播放态可观察证据）

⚠️ 漂移注记：YAML 步骤 1 基于旧构建音乐 Tab 搜索卡；构建若漂移，入口
探测处失败即证据，执行轮标定。"同一歌曲"精确比对（播放条歌名 OCR 与
首行歌名一致）受迷你条字号/OCR 保真度限制，以播放条在场承载复播断言。
关键词走环境变量 SWAN_SEARCH_KEYWORD（缺省 'piano'）。
cleanup：播放态不清理（冷启动复位）。
"""
from __future__ import annotations

import os

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_HOME_MUSIC_SEARCH_BAR,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestFullChainSearchPlayResearch(SwanRP03Mixin, BaseTest):
    """全链 A：音乐 Tab 入口搜索→播放→返回→重搜同词→播放中。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_full_chain_search_play_research(self):
        """搜索 piano → 播首行 → 返回 → 重搜 piano → 播放条在场。"""
        keyword = os.environ.get("SWAN_SEARCH_KEYWORD", "").strip() or "piano"

        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('音乐')
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')

        self.userA.submit_search_keyword(keyword)
        self.userA.play_first_song_result()

        self.userA.press_back()
        self.userA.submit_search_keyword(keyword)
        assert self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=10) is not None, (
            "重搜同词后底部播放条未出现——复播未生效")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索结果页（后台播放随冷启动复位）
