# CASE-ID: player-POS-020
"""Swan 回归·播放器：暂停乐观期与回执落定（player-POS-020）。

步骤 → AW 映射：
- 前置 播放中 → preset_playing("speaker") + open_player_page()
- 步骤1-3 播放中点击暂停至回执落定 → player_control("pause")（暂停键 [图]
  点击，乐观标记→同 id 回执采纳对 UI 不可分辨）+ assert_paused()
  （播放键 [图] + 进度静止双证据，展示稳定暂停）+ read_player_progress()
  （乐观期播放头冻结：进度值定格可读，无跳变）
- 步骤4 快速连点暂停/播放 → 连续 player_control("pause")/("play")/"pause"/"play"
  （调用间无硬等待，T19 规则 2 过期 id 回执丢弃吸收连点）+ assert_playing()
  （终态与最后一次权威命令一致，不错乱）

乐观切换→回执落定全链回归面：快速连点不错乱、「按钮卡暂停但进度在走」禁再现。
清理：停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestPauseOptimisticSettle(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """暂停乐观期与回执落定（POS-020）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_pause_optimistic_settle(self):
        """暂停落定（进度冻结可读）→ 快速连点后终态与最后命令一致。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1-3：暂停乐观切换→回执落定（展示稳定暂停，播放头冻结）
        self.userA.player_control("pause")
        self.userA.assert_paused()
        frozen = self.userA.read_player_progress()
        assert frozen is not None, "暂停后读不到进度双时间（播放头未冻结可读？）"
        # 步骤4：快速连点暂停/播放（过期 id 回执丢弃吸收，无硬等待）
        self.userA.player_control("play")
        self.userA.player_control("pause")
        self.userA.player_control("play")
        # 终态与最后一次权威命令一致
        self.userA.assert_playing()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
