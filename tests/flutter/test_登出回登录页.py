# CASE-ID: aw-登出回登录页
# LINKED-CASE: login-POS-016
"""Swan Flutter 登出回登录页（原 test_swan_login_logout.py，2026-10-12 一用例一文件拆分）。

业务方法复用 SwanBusiness（已实测），用例层只做编排与断言：
- login_by_sms(phone)：验证码登录，已登录自动跳过
- logout_if_needed()：登出回登录页，未登录自动跳过

账号走环境变量 SWAN_PHONE（.env.local），不在用例中硬编码手机号。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
结束状态：未登录（登录页）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan import SwanBusiness
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestLogoutReturnsToLogin(SwanLoginRegressionMixin, BaseTest):
    """登出回登录页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_logout_returns_to_login(self):
        """登出回登录页：确保已登录 → 登出 → 断言登录页（含置灰「下一步」）。"""
        self.userA.login_by_sms(self.userA.phone)
        assert self.userA.accessibility_exists(
            SwanBusiness.KEY_TAB_ME
        ), "前置登录失败，未进入首页"

        self.userA.logout_if_needed()
        self.userA.assert_on_login_page()
        assert not self.userA.accessibility_exists(
            SwanBusiness.KEY_TAB_ME
        ), "登出后首页 tab 仍存在，疑似未真正登出"

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：未登录（登录页）