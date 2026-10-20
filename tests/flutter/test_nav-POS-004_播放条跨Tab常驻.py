# CASE-ID: nav-POS-004
"""Swan 回归·M03 主框架导航：播放会话下迷你播放条跨 Tab 常驻（nav-POS-004）。

用例 → AW 映射：
- 音箱播放会话 → preset_playing("speaker")（落我喜欢页，播放已起）
- 我喜欢页（白名单）播放条在屏 → assert_mini_player_bar_text()
  （播放条 band [OCR] 非空判据——会话态模板 SWAN_BOTTOM_PLAYER_BAR
  内容偏离不可靠，verify-run3 口径）
- 我喜欢页为 push 页，先 press_back() 回壳层再轮切四 Tab：
  首页→平台→设备→我的逐 tab go_bottom_tab() + assert_mini_player_bar_text()
（播放条下方尾部空白双写为像素级布局测量，UI 自动化面不表达。）
清理：无（下条用例冷启动自然接管播放会话）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavPos004BarAcrossTabs(SwanRP01Mixin, BaseTest):
    """播放会话下迷你播放条跨 Tab 常驻（nav-POS-004）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_mini_player_bar_persists_across_tabs(self):
        """四个底部 Tab 轮切，迷你播放条应逐页常驻在屏。"""
        self.userA.preset_playing("speaker")
        self.userA.assert_mini_player_bar_text()
        self.userA.press_back()
        for tab in ("首页", "平台", "设备", "我的"):
            self.userA.go_bottom_tab(tab)
            self.userA.assert_mini_player_bar_text()

    def teardown(self) -> None:
        """无用例私有清理（播放会话由下条用例冷启动自然接管）。"""
        pass
