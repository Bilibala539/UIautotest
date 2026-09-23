"""Swan 回归·播放器域：进度与音量（回归用例 23-28）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例23-24 拖动/点击进度条跳转     → seek_to(ratio, action="drag"|"click")
- 用例25-26 音量弹窗滑条/加减钮调节 → set_volume(value, action=...)
- 用例27-28 物理音量键短按/长按     → volume_key(direction, long_press)

断言口径（方案 §5③ 拍板）：声学断言降级为 UI 态——进度按 OCR 双时间核对
已播 ≈ ratio × 总时长；音量按音量百分比 OCR 核对数值 / 增减方向。
矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）。滑条/进度条一律 drag_on_template 元素锚定，不写坐标。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → go_home。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from tests.flutter.swan_regression_common import DEVICE_TYPES, SwanPlayerRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

SEEK_RATIO = 0.75       # 进度跳转目标比例
VOLUME_TARGET = 40      # drag/click 音量目标（百分比）
VOLUME_STEPS = 3        # plus/minus 连点次数


class TestPlayerSeekAndVolume(SwanPlayerRegressionMixin, BaseTest):
    """播放进度与音量（回归用例 23-28）。"""

    @pytest.mark.parametrize("action", ["drag", "click"])
    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_seek_progress(self, device_type, action):
        """用例23-24：进度条拖动/点击跳转到 75%，OCR 双时间核对落点。"""
        self._preset_playing(device_type)
        self.user.seek_to(SEEK_RATIO, action=action)

    @pytest.mark.parametrize("action", ["drag", "click", "plus", "minus"])
    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_volume_adjust(self, device_type, action):
        """用例25-26：音量弹窗滑条拖/点与加减钮调节（UI 态百分比核对）。"""
        self._preset_playing(device_type)
        value = VOLUME_TARGET if action in ("drag", "click") else VOLUME_STEPS
        self.user.set_volume(value, action=action)

    @pytest.mark.parametrize("long_press,direction",
                             [(False, "up"), (False, "down"), (True, "up")])
    @pytest.mark.parametrize("device_type", DEVICE_TYPES)
    def test_volume_key(self, device_type, direction, long_press):
        """用例27-28：物理音量键短按升/降与长按（百分比增减方向断言）。

        先经音量弹窗把音量拖到中位 50，避免 0%/100% 边界使方向断言失真。
        """
        self._preset_playing(device_type)
        self.user.set_volume(50, action="drag")
        self.user.volume_key(direction=direction, long_press=long_press)
