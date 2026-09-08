"""Swan Flutter 登录、登出流程。"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest


_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_credentials = bool(
    os.environ.get("SWAN_PHONE", "").strip()
    and os.environ.get("SWAN_PASSWORD", "")
)

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_credentials,
    reason="Swan 用例需要 PLATFORM=flutter、SWAN_PHONE 和 SWAN_PASSWORD",
)


class TestSwanLoginLogout(BaseTest):
    """验证 Swan 从登录页登录后再安全退出。"""

    def setup(self):
        self.user = self.users("swan")
        self.phone = os.environ.get("SWAN_PHONE", "").strip()
        self.password = os.environ.get("SWAN_PASSWORD", "")
        package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()
        starter = getattr(self.user.driver, "start_app", None)
        if starter is not None:
            starter(package)
            self.user.aw.sleep(1)

    def _text_present(self, *texts: str, timeout: int = 5) -> bool:
        return any(
            self.user.aw.find_text_by_ocr(text, timeout=timeout) is not None
            for text in texts
        )

    def _assert_logged_out(self) -> None:
        assert self._text_present(
            "密码登入",
            "验证码登入",
            "登入后就可畅享音乐世界",
            timeout=12,
        ), "未回到 Swan 登录页"

    def _login(self) -> None:
        aw = self.user.aw
        if not aw.accessibility_exists("login_password_field"):
            aw.click_text("密码登入", timeout=12)
        aw.click_accessibility("login_phone_field")
        aw.input_text(self.phone)
        aw.click_accessibility("login_password_field")
        aw.input_text(self.password)
        aw.press_back()
        aw.click_accessibility("login_agreement_checkbox")
        aw.click_accessibility("login_submit_button")
        assert self._text_present("推荐", "首页", timeout=20), "登录后未进入首页"

    def _logout(self) -> None:
        aw = self.user.aw
        aw.click_text("我的", timeout=12)
        aw.click_accessibility("me_user_profile_entry")
        aw.click_accessibility("person_info_logout_button")
        self._assert_logged_out()

    def test_login_then_logout(self):
        """从任意初始状态完成一次登录和登出，最终保持未登录。"""
        aw = self.user.aw
        if not aw.accessibility_exists("login_page"):
            self._logout()
        self._login()
        self._logout()

    def teardown(self):
        """用例最终状态由测试流程保证为未登录。"""
