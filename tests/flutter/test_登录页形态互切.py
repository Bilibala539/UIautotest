"""Swan Flutter 登录页两形态互切（原 test_swan_password_login.py，2026-10-12 拆分）。

业务方法复用 SwanBusiness，用例层只做编排与断言：
- logout_if_needed()：登出回登录页，未登录自动跳过

账号走环境变量 SWAN_PHONE / SWAN_PASSWORD（.env.local），用例中不硬编码。
断言优先级：图片断言（image_exists）> key（accessibility/wait_accessibility）> OCR。
密码页无独立图片模板（提交按钮文案"登录"与验证码页"下一步"同 key 不同形态，
SWAN_LOGIN_SUBMIT_BTN 仅匹配"下一步"置灰态），表单形态断言走 key 双重校验。
断言辅助与表单归一化在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
结束状态：未登录（验证码登录页）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan import SwanBusiness
from utils.aw.business.swan_regression import SwanLoginRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())
_has_password = bool(os.environ.get("SWAN_PASSWORD", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone or not _has_password,
    reason="Swan 密码用例需要 PLATFORM=flutter 和 SWAN_PHONE/SWAN_PASSWORD",
)


class TestLoginPageToggle(SwanLoginRegressionMixin, BaseTest):
    """登录页两种形态互切。"""

    def test_login_page_toggle(self):
        """登录页两种形态互切：登出 → 验证码形态 ⇄ 密码形态，断言互斥反转。"""
        self._ensure_fresh_sms_form()

        # 切到密码形态
        self.aw.click_accessibility(SwanBusiness.KEY_USE_PASSWORD_BUTTON)
        self._assert_password_form()

        # 切回验证码形态，互斥反转
        self.aw.click_accessibility(SwanBusiness.KEY_USE_SMS_BUTTON)
        self._assert_sms_form()
        # 结束状态：未登录（验证码登录页）
