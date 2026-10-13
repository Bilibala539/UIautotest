"""Swan 回归·播放器域：物理音量键短按/长按（回归用例 27-28）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例27-28 物理音量键短按/长按 → volume_key(direction, long_press)

断言口径（方案 §5③ 拍板）：声学断言降级为 UI 态——音量按百分比增减方向
断言。
矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → 输出恢复 → 回首页（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin



class TestVolumeKey(SwanPlayerRegressionMixin, BaseTest):
    """物理音量键短按/长按（回归用例 27-28）。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def test_volume_key(self):
        """用例27-28：物理音量键短按升/降与长按（百分比增减方向断言）。

        先经音量弹窗把音量拖到中位 50，避免 0%/100% 边界使方向断言失真。
        """
        long_press = True
        direction = 'up'
        self._preset_playing(device_type)
        self.user.set_volume(50, action="drag")
        self.user.volume_key(direction=direction, long_press=long_press)

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()