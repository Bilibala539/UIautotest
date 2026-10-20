# CASE-ID: launch-POS-002
"""Swan 回归·M01 启动与隐私：同意隐私协议进入登录页（launch-POS-002）。

用例 → AW 映射：
- 冷启动弹出隐私弹层 → 夹具冷启动 + privacy_dialog_visible() 探测
- 点击「同意」→ accept_privacy_dialog()（点同意+断言弹层关闭）
- 进入登录页 → assert_on_login_page()（登录页锚点断言）
状态条件：需全新安装未同意态窗口（privacyRequired）；135 常态已同意
直接落登录页，弹层不可见即 skip。
清理：无（同意态即常态，后续用例自然衔接）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchPos002AgreeGoesLogin(SwanRP01Mixin, BaseTest):
    """同意隐私协议进入登录页（launch-POS-002）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_accept_privacy_lands_login_page(self):
        """点击「同意」后应进入登录页。"""
        if not self.userA.privacy_dialog_visible(timeout=3):
            pytest.skip("隐私弹层不可见（账号已同意态）——需全新安装未同意窗口")
        self.userA.accept_privacy_dialog()
        self.userA.assert_on_login_page()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
