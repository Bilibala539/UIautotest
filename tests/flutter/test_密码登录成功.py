"""Swan Flutter 密码登录成功（原 test_swan_password_login.py，2026-10-12 一用例一文件拆分）。

业务方法复用 SwanBusiness：
- login_with_password(phone, password)：密码登录，自动从验证码页形态切到密码页

账号走环境变量 SWAN_PHONE / SWAN_PASSWORD（.env.local），用例中不硬编码。
密码页无独立图片模板（提交按钮文案"登录"与验证码页"下一步"同 key 不同形态），
表单前置归一化在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
结束状态：已登录停在首页（与设备初始状态一致）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())
_has_password = bool(os.environ.get("SWAN_PASSWORD", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone or not _has_password,
    reason="Swan 密码用例需要 PLATFORM=flutter 和 SWAN_PHONE/SWAN_PASSWORD",
)


class TestPasswordLoginSuccess(SwanLoginRegressionMixin, BaseTest):
    """密码登录成功。"""

    def test_password_login_success(self):
        """密码登录成功：确保未登录 → 密码页输手机号/密码 → 勾协议 → 登录 → 进首页。"""
        self._ensure_fresh_sms_form()

        self.user.login_with_password(self.phone, self.password)
        self._assert_on_home()
        # 结束状态：已登录停在首页
