"""Swan Flutter 密码登录闭环（表单互切 + 密码登录成功 + 错误密码拒绝）。

业务方法复用 SwanBusiness：
- login_with_password(phone, password)：密码登录，自动从验证码页形态切到密码页
- logout_if_needed()：登出回登录页，未登录自动跳过
- login_by_sms(phone)：验证码登录（收尾恢复登录态用）

账号走环境变量 SWAN_PHONE / SWAN_PASSWORD（.env.local），用例中不硬编码。

断言优先级：图片断言（image_exists）> key（accessibility/wait_accessibility）> OCR。
密码页无独立图片模板（提交按钮文案"登录"与验证码页"下一步"同 key 不同形态，
SWAN_LOGIN_SUBMIT_BTN 仅匹配"下一步"置灰态），表单形态断言走 key 双重校验。

⚠️ 安全约束：连续 3 次密码错误可能锁号——test_wrong_password_rejected 全程只试 1 次。
收尾约定：无论走哪条路径，模块结束状态为「已登录停在首页」（与设备初始状态一致），
由 test_wrong_password_rejected 末尾"重启重置表单 + login_by_sms"恢复（若该用例被
跳过，test_password_login_success 已停在首页，状态一致）。重启重置的原因：提交失败
后的登录页表单会残留已填文本与协议勾选态，login_by_sms 盲点协议会反选导致
「下一步」置灰、验证码发不出去（2026-09-08 实测踩坑）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_BOTTOM_PLAYER_BAR
from utils.aw.business.swan import SwanBusiness

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())
_has_password = bool(os.environ.get("SWAN_PASSWORD", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone or not _has_password,
    reason="Swan 密码用例需要 PLATFORM=flutter 和 SWAN_PHONE/SWAN_PASSWORD",
)


class TestSwanPasswordLogin(BaseTest):
    """Swan 密码登录：表单互切 / 登录成功 / 错误密码拒绝。"""

    def setup(self):
        self.user = self.users("swan")
        self.aw = self.user.aw  # 业务层实例 = 基础操作 + SwanBusiness 业务方法
        self.phone = self.user.phone
        self.password = os.environ.get("SWAN_PASSWORD", "").strip()
        self.package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()

    # ---------- 断言辅助 ----------

    def _assert_on_home(self, timeout: float = 20.0) -> None:
        """首页断言：tab_me key + 底部播放条图片（双重校验）。"""
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_TAB_ME, timeout=timeout
        ), "未进入首页（tab_me 未出现）"
        self.aw.image_exists(SWAN_BOTTOM_PLAYER_BAR, timeout=10)

    def _assert_sms_form(self, timeout: float = 15.0) -> None:
        """验证码登录页形态：password_field 不存在 + use_password_button 存在。"""
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_USE_PASSWORD_BUTTON, timeout=timeout
        ), "验证码登录形态断言失败（login_use_password_button 未出现）"
        assert not self.aw.accessibility_exists(
            SwanBusiness.KEY_PASSWORD_FIELD
        ), "验证码登录形态下出现了密码输入框，形态互斥被破坏"

    def _assert_password_form(self, timeout: float = 15.0) -> None:
        """密码登录页形态：password_field 存在 + use_password_button 不存在
        + use_sms_button 存在（三重 key 校验）。"""
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_PASSWORD_FIELD, timeout=timeout
        ), "密码登录形态断言失败（login_password_field 未出现）"
        assert not self.aw.accessibility_exists(
            SwanBusiness.KEY_USE_PASSWORD_BUTTON
        ), "密码登录形态下仍存在「密码登入」切换按钮，形态互斥被破坏"
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_USE_SMS_BUTTON
        ), "密码登录形态下缺少「验证码登入」反向切换按钮"

    def _ensure_fresh_sms_form(self):
        """前置归一化：确保停在全新验证码登录形态（空表单、协议未勾选）。

        - 已登录（tab_me 存在）→ 先登出回登录页
        - 未登录但停在脏表单（密码形态 / 有错误提示残留，上一轮中断遗留）
          → 重启 App 重置（实测登录页表单无持久化，重启回到全新验证码形态）
        """
        if self.aw.accessibility_exists(SwanBusiness.KEY_TAB_ME):
            self.user.logout_if_needed()
        if (self.aw.accessibility_exists(SwanBusiness.KEY_PASSWORD_FIELD)
                or self.aw.accessibility_exists(SwanBusiness.KEY_ERROR_TEXT)):
            self.user.driver.stop_app(self.package)
            self.user.driver.start_app(self.package)
            assert self.aw.wait_accessibility(
                SwanBusiness.KEY_LOGIN_PAGE, timeout=30
            ), "重启 App 后未回到登录页"
        self._assert_sms_form()

    # ---------- 用例 ----------

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

    def test_password_login_success(self):
        """密码登录成功：确保未登录 → 密码页输手机号/密码 → 勾协议 → 登录 → 进首页。"""
        self._ensure_fresh_sms_form()

        self.user.login_with_password(self.phone, self.password)
        self._assert_on_home()
        # 结束状态：已登录停在首页

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
