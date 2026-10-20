# CASE-ID: player-NEG-030
"""Swan 回归·播放器：进度拖动首尾边界与快速连拖（player-NEG-030）。

步骤 → AW 映射：
- 前置 播放中 → preset_playing("speaker")
- 步骤1/2 拖到头（seek=duration，near-end 放行归零路径协同）→ seek_to(0.98)
  （进度条 [图] 整条锚定拖拽，OCR 双时间核对 已播≈ratio×总时长，
  容差 max(5s, 总时长 10%)，进度保留目标位不回拖）
- 步骤3 拖回头部归零（seek=0，归零播放无回退抖动循环）→ seek_to(0.02) +
  assert_playing()
- 步骤4 连续快速拖拽 3 次（命令不积压死锁）→ 连续 seek_to(0.5)/(0.8)/(0.3)（
  调用间无硬等待）+ assert_playing() + read_player_progress()（终态与设备真值一致）

seek 双端边界回归面：拖到头走钳制+兜底解锁+无双闪；拖回头部正常；
与 near-end 防归零守卫协同一致。
清理：写副作用还原——显式停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestSeekEdgesAndRapidDrags(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """进度拖动首尾边界与快速连拖（NEG-030）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_seek_edges_and_rapid_drags(self):
        """拖到曲末 → 拖回头部归零 → 三连快拖 → 播放态与进度真值一致。"""
        self.userA.preset_playing("speaker")
        # 步骤1/2：拖到曲末（钳制+near-end 放行，进度保留目标位不回拖）
        self.userA.seek_to(0.98)
        # 步骤3：拖回头部归零播放（无回退抖动循环）
        self.userA.seek_to(0.02)
        self.userA.assert_playing()
        # 步骤4：三连快拖（调用间无硬等待，命令队列不积压死锁）
        self.userA.seek_to(0.5)
        self.userA.seek_to(0.8)
        self.userA.seek_to(0.3)
        self.userA.assert_playing()
        progress = self.userA.read_player_progress()
        assert progress is not None, "连拖后 OCR 读不到进度双时间（终态与设备真值失联？）"
        elapsed, total = progress
        assert 0 <= elapsed <= total, (
            f"连拖后进度越界：已播 {elapsed}s / 总 {total}s")
        # 清理：写副作用还原——显式停止播放
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
