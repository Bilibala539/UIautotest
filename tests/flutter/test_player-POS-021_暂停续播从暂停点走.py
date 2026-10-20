# CASE-ID: player-POS-021
"""Swan 回归·播放器：暂停续播从暂停点走（sticky+守卫 D）（player-POS-021）。

步骤 → AW 映射：
- 前置 播放中 → preset_playing("speaker")
- 步骤1 暂停并记录进度值 p → player_control("pause") + assert_paused()
  （暂停落定）+ read_player_progress()（进度停在 p）
- 步骤2 恢复播放 → player_control("play") + assert_playing()（守卫 D 2000ms
  容差内续走）+ read_player_progress()（从 p 附近续走：已播 ≥ p-2s 且
  ≤ p+15s——绝不归零重启）
- 步骤3 续播稳定性（约 10s 窗）→ assert_playing() 复核（进度持续推进、
  按钮保持 playing，由封面动检/进度递增双证据覆盖）

暂停-恢复闭环回归面：进度连续不归零，无「按钮卡暂停但进度在走」形态。
清理：停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestResumeFromPausePoint(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """暂停续播从暂停点走（POS-021）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_resume_from_pause_point(self):
        """暂停记录进度 p → 恢复 → 进度从 p 附近续走绝不归零。"""
        self.userA.preset_playing("speaker")
        # 步骤1：暂停落定并记录进度值 p
        self.userA.player_control("pause")
        self.userA.assert_paused()
        paused_at = self.userA.read_player_progress()
        assert paused_at is not None, "暂停后读不到进度双时间（进度停在 p 不可证）"
        # 步骤2/3：恢复播放，进度从 p 附近续走（守卫 D 容差），绝不归零重启
        self.userA.player_control("play")
        self.userA.assert_playing()
        resumed = self.userA.read_player_progress()
        assert resumed is not None, "恢复后读不到进度双时间"
        assert resumed[0] >= paused_at[0] - 2, (
            f"续播进度回跳越过守卫容差：暂停点 {paused_at[0]}s → 恢复后 "
            f"{resumed[0]}s（归零重启？）")
        assert resumed[0] <= paused_at[0] + 15, (
            f"续播进度跳变：暂停点 {paused_at[0]}s → 恢复后 {resumed[0]}s")
        # 步骤3：续播稳定性复核（进度持续推进、按钮保持 playing）
        self.userA.assert_playing()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
