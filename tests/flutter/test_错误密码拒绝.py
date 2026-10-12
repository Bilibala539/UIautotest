"""Swan Flutter 错误密码被拒绝（原 test_swan_password_login.py，2026-10-12 拆分）。

业务方法复用 SwanBusiness，用例层只做编排与断言。

⚠️ 安全约束：连续 3 次密码错误可能锁号——本用例全程只试 1 次。
收尾约定：提交失败后的登录页表单会残留已填文本与协议勾选态，login_by_sms
盲点协议会反选导致「下一步」置灰、验证码发不出去（2026-09-08 实测踩坑），
故收尾重启 App 重置表单后再 login_by_sms 恢复登录态。
账号走环境变量 SWAN_PHONE / SWAN_PASSWORD（.env.local），用例中不硬编码。
断言辅助与表单归一化在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
结束状态：已登录停在首页（与设备初始状态一致）。
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


class TestWrongPasswordRejected(SwanLoginRegressionMixin, BaseTest):
    """错误密码被拒绝（只试 1 次，防锁号）。"""

    def test_wrong_password_rejected(self):
        """错误密码被拒绝（只试 1 次，防锁号）：断言未进首页且出现
        login_error_text 错误提示，收尾重启重置表单后 login_by_sms 恢复登录态。"""
        self._ensure_fresh_sms_form()

        # 切到密码形态，输入正确手机号 + 错误密码
        self.aw.click_accessibility(SwanBusiness.KEY_USE_PASSWORD_BUTTON)
        self._assert_password_form()
        self.aw.click_accessibility(SwanBusiness.KEY_PHONE_FIELD)
        self.aw.clear_input()
        self.aw.input_text(self.phone)
        self.aw.click_accessibility(SwanBusiness.KEY_PASSWORD_FIELD)
        self.aw.clear_input()
        self.aw.input_text("000000")
        self.aw.press_back()  # 收键盘（实测只收键盘不退出 App）
        self.aw.click_accessibility(SwanBusiness.KEY_AGREEMENT)
        self.aw.click_accessibility(SwanBusiness.KEY_SUBMIT)

        # 断言未进首页：错误密码不应跳转首页
        assert not self.aw.wait_accessibility(
            SwanBusiness.KEY_TAB_ME, timeout=8
        ), "错误密码竟进入了首页（tab_me 出现），登录校验失效！"

        # 断言出现错误提示（实测：错误文案非 toast，是常驻节点
        # login_error_text，content-desc"密码错误，请重新输入！"）
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_ERROR_TEXT
        ), "错误密码后未出现 login_error_text 错误提示"

        # 收尾：提交失败后的登录页表单有残留（已填文本 + 协议已勾选，
        # login_by_sms 再点协议会反选导致"下一步"置灰），重启 App 重置表单
        # （登录页无状态持久化，重启回到全新验证码登录形态）
        self.user.driver.stop_app(self.package)
        self.user.driver.start_app(self.package)
        self._assert_sms_form(timeout=30)
        self.user.login_by_sms(self.phone)
        self._assert_on_home()
