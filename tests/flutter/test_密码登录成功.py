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
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_password_login_success(self):
        """密码登录成功：确保未登录 → 密码页输手机号/密码 → 勾协议 → 登录 → 进首页。"""
        self.userA.ensure_fresh_sms_form()

        self.userA.login_with_password(self.userA.phone, self.userA.password)
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在首页