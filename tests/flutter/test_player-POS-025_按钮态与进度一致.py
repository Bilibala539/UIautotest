# CASE-ID: player-POS-025
"""Swan 回归·播放器：按钮态与进度一致（缓冲不翻态）（player-POS-025）。

步骤 → AW 映射：
- 前置 播放中 → preset_playing("speaker") + open_player_page()
- 步骤1 播放中按钮态与进度联动 → assert_playing()（暂停键 [图]=playing 语义）
  + read_player_progress()（进度双时间可读；推进证据由 assert_playing 的
  封面动检/进度递增双证据覆盖）
- 步骤2 播放中持续观察（含自然缓冲窗口期）→ assert_playing() 二次复核
  （缓冲不翻按钮态——T19 规则 4 保持 playing，不卡暂停假象；自然缓冲
  窗口不可定时注入，由复核窗口覆盖）

按钮态与进度一致性回归面：缓冲不是暂停，「按钮卡暂停但进度在走」禁再现。
清理：停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestButtonStateProgressConsistency(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """按钮态与进度一致（缓冲不翻态）（POS-025）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_button_state_progress_consistency(self):
        """播放中按钮=playing 且进度推进，复核窗口内不翻态。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1：按钮 playing 语义 + 进度可读（联动一致）
        self.userA.assert_playing()
        progress = self.userA.read_player_progress()
        assert progress is not None, "播放中读不到进度双时间（联动失证）"
        # 步骤2：持续观察复核（含自然缓冲窗口期，缓冲不翻按钮态）
        self.userA.assert_playing()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
