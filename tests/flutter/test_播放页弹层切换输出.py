"""Swan 回归·播放器域：播放页设备弹层切换输出（回归用例 12）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例12 播放页设备弹层切换输出 → select_device(via="player")

前置：已登录 + 账号绑定的 rig 设备在线（方案 §5④）。
目标设备名经 SWAN_DEVICE_NAME 注入，默认 Libretto_0E00（知识库实测绑定设备）。
⚠️ 输出设备切换真实生效且跨用例保留（方法层不做自动回切，rig 复位由
mixin teardown 的输出恢复 + 设备管理流程负责）；真点真音箱口径见方案 §5②。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：关残留弹层 → 尽力暂停 → 收播放页 → 输出恢复 → 回首页（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestSwitchDeviceFromPlayerSheet(SwanPlayerRegressionMixin, BaseTest):
    """播放页设备弹层切换输出（回归用例 12）。"""

    def test_switch_device_from_player_sheet(self):
        """用例12：播放页右上角开设备弹层点目标设备行，断言勾选态 [图]。"""
        self._open_player_page()
        self.user.select_device(self.DEVICE_NAME, via="player")
