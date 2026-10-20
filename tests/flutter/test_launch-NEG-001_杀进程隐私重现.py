# CASE-ID: launch-NEG-001
"""Swan 回归·M01 启动与隐私：首启弹窗未决杀进程，重启仍须同意（launch-NEG-001）。

用例 → AW 映射：
- 冷启动至隐私弹层 → 夹具冷启动 + privacy_dialog_visible() 探测
- 返回键不可退出弹层 → press_back() + 弹层仍在断言
- 不点同意直接 force-stop → force_stop_cold_start()（不做弹窗处置的特殊冷启动）
- 重新冷启动弹层重现 → privacy_dialog_visible() 断言
状态条件：需全新安装未同意态窗口（privacyRequired）；135 常态已同意，
弹层不可见即 skip（同 test_冷启动落登录页.py 条件用例口径）。
清理（YAML cleanup）：teardown 点击「同意」恢复同意态，供后续用例衔接。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchNeg001PrivacySurvivesKill(SwanRP01Mixin, BaseTest):
    """首启弹窗未决杀进程，重启仍须同意（launch-NEG-001）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_privacy_dialog_survives_force_stop(self):
        """未同意态下不点同意杀进程重启，隐私弹层必须重现。"""
        if not self.userA.privacy_dialog_visible(timeout=3):
            pytest.skip("隐私弹层不可见（账号已同意态）——需全新安装未同意窗口")
        self.userA.press_back()
        assert self.userA.privacy_dialog_visible(timeout=2), (
            "返回键退出了隐私弹层（canPop=false 强制应答被破坏）")
        self.userA.force_stop_cold_start()
        assert self.userA.privacy_dialog_visible(timeout=10), (
            "杀进程重启后隐私弹层未重现（同意标记被提前写回）")

    def teardown(self) -> None:
        """用例私有清理（YAML cleanup）：点击「同意」恢复同意态。"""
        if self.userA.privacy_dialog_visible(timeout=2):
            self.userA.accept_privacy_dialog()
