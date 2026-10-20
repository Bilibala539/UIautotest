# CASE-ID: launch-POS-009
"""Swan 回归·M01 启动与隐私：隐私协议弹层返回键拦截（launch-POS-009）。

用例 → AW 映射：
- 冷启动弹出隐私弹层 → 夹具冷启动 + privacy_dialog_visible() 探测
- 按返回键弹层不消失、不退出应用 → press_back() + 弹层仍在断言（二次）
状态条件：需全新安装未同意态窗口（privacyRequired）；135 常态已同意
无弹层，不可见即 skip。
清理（YAML cleanup）：teardown 点击「同意」恢复同意态，供后续用例衔接。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchPos009BackBlocksPrivacy(SwanRP01Mixin, BaseTest):
    """隐私协议弹层返回键拦截（launch-POS-009）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_back_key_keeps_privacy_dialog(self):
        """返回键应被拦截：弹层仍在屏、应用不退出。"""
        if not self.userA.privacy_dialog_visible(timeout=3):
            pytest.skip("隐私弹层不可见（账号已同意态）——需全新安装未同意窗口")
        self.userA.press_back()
        assert self.userA.privacy_dialog_visible(timeout=2), (
            "第一次返回后弹层消失或应用退出（返回键未被拦截）")
        self.userA.press_back()
        assert self.userA.privacy_dialog_visible(timeout=2), (
            "第二次返回后弹层消失或应用退出（连续返回应同样被拦截）")

    def teardown(self) -> None:
        """用例私有清理（YAML cleanup）：点击「同意」恢复同意态。"""
        if self.userA.privacy_dialog_visible(timeout=2):
            self.userA.accept_privacy_dialog()
