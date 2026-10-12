"""Swan Flutter 登录态跨进程重启持久化（原 test_swan_login_logout.py，2026-10-12 拆分）。

业务方法复用 SwanBusiness（已实测），用例层只做编排与断言：
- login_by_sms(phone)：验证码登录，已登录自动跳过
- logout_if_needed()：登出回登录页，未登录自动跳过

账号走环境变量 SWAN_PHONE（.env.local），不在用例中硬编码手机号。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
结束状态：未登录（登录页），后续用例起点干净。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestLoginStatePersistsRestart(SwanLoginRegressionMixin, BaseTest):
    """登录态跨进程重启持久化。"""

    def test_login_state_persists_restart(self):
        """登录态跨进程重启持久化：杀 App 重启后仍在首页，收尾登出。"""
        # 前置登录（未登录则补登录）
        self.user.login_by_sms(self.phone)
        self._assert_on_home()

        self.user.driver.stop_app(self.package)
        self.user.driver.start_app(self.package)
        self._assert_on_home(timeout=30)  # 冷启动约 5s，等 tab_me + 底部播放条

        self.user.logout_if_needed()  # 收尾登出，保持后续用例起点干净
