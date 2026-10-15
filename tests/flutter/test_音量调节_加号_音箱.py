# CASE-ID: aw-音量调节_加号_音箱
# LINKED-CASE: REG-025,REG-026
"""Swan 回归·播放器域：音量弹窗滑条/加减钮调节（回归用例 25-26）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例25-26 音量弹窗滑条/加减钮调节 → set_volume(value, action=...)

断言口径（方案 §5③ 拍板）：声学断言降级为 UI 态——音量按音量百分比 OCR
核对数值。
矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）。滑条一律 drag_on_template 元素锚定，不写坐标。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → 输出恢复 → 回首页（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin


VOLUME_TARGET = 40  # drag/click 音量目标（百分比）
VOLUME_STEPS = 3    # plus/minus 连点次数


class TestVolumeAdjust(SwanPlayerRegressionMixin, BaseTest):
    """音量弹窗滑条/加减钮调节（回归用例 25-26）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_volume_adjust(self):
        """用例25-26：音量弹窗滑条拖/点与加减钮调节（UI 态百分比核对）。"""
        self.userA.preset_playing('wifi_device')
        self.userA.set_volume(VOLUME_STEPS, action='plus')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
