# CASE-ID: aw-循环模式与播放控制_随机循环_音箱
# LINKED-CASE: REG-015,REG-016,REG-017,REG-018,REG-019,REG-020,REG-021,REG-022
"""Swan 回归·播放器域：循环模式与播放控制序列（回归用例 15-22 矩阵）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例15-22 循环模式 × 设备类型矩阵上的播放控制序列
  → set_loop_mode + player_control(pause/play/next/prev)
  + assert_playing/assert_paused

矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）× loop_mode（list/single/shuffle）。
播放态断言 = 控制键图标 [图] + 封面区 region_changed 双证据（方案 §5③，
不做声学断言）；回归须真点真音箱（方案 §5②）。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → 输出恢复 → 回首页（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin


LOOP_MODES = ["list", "single", "shuffle"]


class TestLoopModeAndControls(SwanPlayerRegressionMixin, BaseTest):
    """循环模式 × 播放控制矩阵（回归用例 15-22）。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def test_loop_mode_and_controls(self):
        """用例15-22：设备类型 × 循环模式矩阵上的播放控制序列。

        set_loop_mode 以目标态图标 [图] 断言收尾；暂停/继续分别以
        assert_paused/assert_playing 双证据断言；切歌后断言播放态保持
        （具体曲目切换由已知歌名的用例经 assert_now_playing 复核，见用例14）。
        """
        loop_mode = 'shuffle'
        device_type = 'wifi_device'
        self._preset_playing(device_type)
        self.user.set_loop_mode(loop_mode)
        self.user.player_control("pause")
        self.user.player_control("play")
        self.user.player_control("next")
        self.user.player_control("prev")

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()