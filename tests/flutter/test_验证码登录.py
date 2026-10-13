"""Swan Flutter 验证码登录成功（原 test_swan_login_logout.py，2026-10-12 一用例一文件拆分）。

业务方法复用 SwanBusiness（已实测），用例层只做编排与断言：
- logout_if_needed()：登出回登录页，未登录自动跳过
- login_by_sms(phone)：验证码登录，已登录自动跳过

账号走环境变量 SWAN_PHONE（.env.local），不在用例中硬编码手机号。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
已知限制：SWAN_LOGIN_SUBMIT_BTN 模板是「下一步」按钮的置灰态，仅用于登录页
存在性断言；点「下一步」必须走业务方法内的 key ``login_submit_button``。
结束状态：已登录停在首页（G3/G4 允许）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestSmsLoginSuccess(SwanLoginRegressionMixin, BaseTest):
    """验证码登录成功。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()


    def test_sms_login_success(self):
        """验证码登录成功：登出确保未登录 → 取码登录 → 断言进首页。"""
        self.user.logout_if_needed()
        self._assert_on_login_page()
        self.user.login_by_sms(self.phone)
        self._assert_on_home()
        # 结束状态：已登录停在首页（G3/G4 允许），后续用例直接复用该登录态
