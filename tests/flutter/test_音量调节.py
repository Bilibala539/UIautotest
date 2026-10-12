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
from utils.aw.business.swan_regression import DEVICE_TYPES, SwanPlayerRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

VOLUME_TARGET = 40  # drag/click 音量目标（百分比）
VOLUME_STEPS = 3    # plus/minus 连点次数


class TestVolumeAdjust(SwanPlayerRegressionMixin, BaseTest):
    """音量弹窗滑条/加减钮调节（回归用例 25-26）。"""

    @pytest.mark.parametrize("action", ["drag", "click", "plus", "minus"])
    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_volume_adjust(self, device_type, action):
        """用例25-26：音量弹窗滑条拖/点与加减钮调节（UI 态百分比核对）。"""
        self._preset_playing(device_type)
        value = VOLUME_TARGET if action in ("drag", "click") else VOLUME_STEPS
        self.user.set_volume(value, action=action)
