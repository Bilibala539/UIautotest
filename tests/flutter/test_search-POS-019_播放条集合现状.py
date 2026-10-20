# CASE-ID: search-POS-019
"""Swan 回归·搜索：搜索域底部播放条集合现状(search-POS-019)。

步骤→AW 映射：
- 进搜索输入页 → open_search_input_page（推荐 Tab 搜索条；YAML 原文为
  音乐 Tab 入口，verify R2 拍板搜索条已回归推荐 Tab，按现状口径转换）
- 断言输入页无底部播放条 → find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2)
  is None
- 搜索并播放结果首行 → submit_search_keyword(keyword) +
  play_first_song_result()（mixin：OCR 首歌曲行动态点击 + 播放条 [图]
  出现断言）
- 返回断言播放条消失 → press_back + find_image(...) is None

⚠️ 注记：关键词走环境变量 SWAN_SEARCH_KEYWORD（缺省 'piano'，需账号
授权态有结果），与既有搜索用例同口径；播放态不清理（冷启动复位）。
cleanup：无用例私有清理（teardown body 一律 pass）。
"""
from __future__ import annotations

import os

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_HOME_MUSIC_SEARCH_BAR,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestSearchPlayerBarStates(SwanRP03Mixin, BaseTest):
    """播放条集合现状：输入页无 → 播放后结果页有 → 返回搜索页无。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_search_player_bar_states(self):
        """输入页无播放条 → 播放首行结果出现 → 返回后消失。"""
        keyword = os.environ.get("SWAN_SEARCH_KEYWORD", "").strip() or "piano"

        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        assert self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is None, (
            "搜索输入页出现底部播放条（未播放不应在场）")

        self.userA.submit_search_keyword(keyword)
        self.userA.play_first_song_result()

        self.userA.press_back()
        assert self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is None, (
            "返回搜索页后底部播放条仍可见（YAML 预期搜索域不驻留播放条）")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索历史态（后台播放随冷启动复位）
