# CASE-ID: aw-播放全部发起播放_手机扬声器
# LINKED-CASE: player-POS-026,player-POS-001,player-POS-004
"""Swan 回归·播放器域：我喜欢页「播放全部」发起播放（回归用例 13）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例13 我喜欢页「播放全部」发起播放 → start_play(mode="all") + 播放态双证据

矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）。
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



class TestPlayAllFromFavorite(SwanPlayerRegressionMixin, BaseTest):
    """我喜欢页「播放全部」发起播放（回归用例 13）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_play_all_from_favorite(self):
        """用例13：我喜欢页「播放全部」发起播放，断言播放态双证据。"""
        self.userA.preset_playing('speaker')
        self.userA.assert_playing()  # 显式复核（start_play 收尾已断言一次）

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
