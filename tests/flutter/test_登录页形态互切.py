# CASE-ID: aw-登录页形态互切
# LINKED-CASE: login-POS-009
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
from image.image_name_mapping import SWAN_PWD_SMS_TOGGLE
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestLoginPageToggle(SwanLoginRegressionMixin, BaseTest):
    """登录页两种形态互切。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_login_page_toggle(self):
        """登录页两种形态互切：登出 → 验证码形态 ⇄ 密码形态，断言互斥反转。

        2026-10-13 key 迁移：形态切换用 [OCR]「密码登入」/ SWAN_PWD_SMS_TOGGLE
        [图]（回切钮）；互斥判定走 mixin 断言辅助（[图]+[OCR] 组合）。
        """
        self.userA.ensure_fresh_sms_form()

        # 切到密码形态（[OCR]；灰胶囊图与「验证码登入」同形互扰，禁用图模板）
        self.userA.click_text("密码登入", timeout=10)
        self.userA.assert_password_form()

        # 切回验证码形态，互斥反转（[OCR] 回切钮文案——图模板有两态渲染漏判）
        self.userA.click_text("验证码登入", timeout=10)
        self.userA.assert_sms_form()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：未登录（验证码登录页）