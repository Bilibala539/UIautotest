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



class TestPasswordLoginSuccess(SwanLoginRegressionMixin, BaseTest):
    """密码登录成功。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户与基础操作入口。"""
        self.user = self.users("swanuserA")
        self.aw = self.user.aw
        self.phone = self.user.phone
        self.password = os.environ.get("SWAN_PASSWORD", "").strip()
        self.package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()

    def test_password_login_success(self):
        """密码登录成功：确保未登录 → 密码页输手机号/密码 → 勾协议 → 登录 → 进首页。"""
        self._ensure_fresh_sms_form()

        self.user.login_with_password(self.phone, self.password)
        self._assert_on_home()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()
        # 结束状态：已登录停在首页