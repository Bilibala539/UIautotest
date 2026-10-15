# CASE-ID: aw-设备页卡片切换输出
# LINKED-CASE: player-POS-032,player-POS-033,device-POS-026
"""Swan 回归·播放器域：设备页点设备卡片切换输出（回归用例 11）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例11 设备页点设备卡片切换输出 → select_device(via="card")

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



class TestSwitchDeviceFromDevicePageCard(SwanPlayerRegressionMixin, BaseTest):
    """设备页点设备卡片切换输出（回归用例 11）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_switch_device_from_device_page_card(self):
        """用例11：设备页点目标设备卡片，断言卡片选中态 [图]。"""
        self.userA.open_device_page()
        self.userA.select_device(self.DEVICE_NAME, via="card")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
