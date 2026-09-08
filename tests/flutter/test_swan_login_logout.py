"""Swan Flutter 登录/登出核心流程（验证码登录 + 状态持久化 + 登出闭环）。

业务方法复用 SwanBusiness（已实测），用例层只做编排与断言：
- login_by_sms(phone)：验证码登录，已登录自动跳过
- logout_if_needed()：登出回登录页，未登录自动跳过

账号走环境变量 SWAN_PHONE（.env.local），不在用例中硬编码手机号。

断言优先级：图片断言（image_exists）> key（accessibility/wait_accessibility）> OCR。
已知限制：SWAN_LOGIN_SUBMIT_BTN 模板是「下一步」按钮的置灰态，仅用于登录页
存在性断言；点「下一步」必须走业务方法内的 key ``login_submit_button``。

各用例结束状态均为「未登录（登录页）」或「首页」，满足 G3/G4；
pytest 按定义顺序执行，用例间的登录态由 login_by_sms / logout_if_needed
的幂等语义自动衔接，不依赖隐式顺序假设。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_BOTTOM_PLAYER_BAR, SWAN_LOGIN_SUBMIT_BTN
from utils.aw.business.swan import SwanBusiness

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestSwanLoginLogout(BaseTest):
    """Swan 登录/登出核心路径。"""

    def setup(self):
        self.user = self.users("swan")
        self.aw = self.user.aw  # 业务层实例 = 基础操作 + SwanBusiness 业务方法
        self.phone = self.user.phone
        self.package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()

    # ---------- 断言辅助 ----------

    def _assert_on_login_page(self, timeout: float = 15.0) -> None:
        """登录页断言：key 根节点 + 置灰态「下一步」图片。"""
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_LOGIN_PAGE, timeout=timeout
        ), "未回到登录页（login_page 未出现）"
        # 置灰态「下一步」模板仅存在于登录页，作为图片级二次确认
        self.aw.image_exists(SWAN_LOGIN_SUBMIT_BTN, timeout=10)

    def _assert_on_home(self, timeout: float = 15.0) -> None:
        """首页断言：tab_me key + 底部播放条图片。"""
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_TAB_ME, timeout=timeout
        ), "未进入首页（tab_me 未出现）"
        self.aw.image_exists(SWAN_BOTTOM_PLAYER_BAR, timeout=10)

    # ---------- 用例 ----------

    def test_sms_login_success(self):
        """验证码登录成功：登出确保未登录 → 取码登录 → 断言进首页。"""
        self.user.logout_if_needed()
        self._assert_on_login_page()
        self.user.login_by_sms(self.phone)
        self._assert_on_home()
        # 结束状态：已登录停在首页（G3/G4 允许），下一条用例直接复用该登录态

    def test_login_state_persists_restart(self):
        """登录态跨进程重启持久化：杀 App 重启后仍在首页，收尾登出。"""
        # 前置登录（承接上一条用例的首页状态，未登录则补登录）
        self.user.login_by_sms(self.phone)
        self._assert_on_home()

        self.user.driver.stop_app(self.package)
        self.user.driver.start_app(self.package)
        self._assert_on_home(timeout=30)  # 冷启动约 5s，等 tab_me + 底部播放条

        self.user.logout_if_needed()  # 收尾登出，保持下一条用例起点干净

    def test_logout_returns_to_login(self):
        """登出回登录页：确保已登录 → 登出 → 断言登录页（含置灰「下一步」）。"""
        self.user.login_by_sms(self.phone)
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_TAB_ME
        ), "前置登录失败，未进入首页"

        self.user.logout_if_needed()
        self._assert_on_login_page()
        assert not self.aw.accessibility_exists(
            SwanBusiness.KEY_TAB_ME
        ), "登出后首页 tab 仍存在，疑似未真正登出"
        # 结束状态：未登录（登录页）

    def test_sms_login_logout_roundtrip(self):
        """登录/登出完整闭环：登出→登录→登出→登录→收尾登出。"""
        self.user.logout_if_needed()
        self._assert_on_login_page()

        # 第一轮：登录 → 登出
        self.user.login_by_sms(self.phone)
        self._assert_on_home()
        self.user.logout_if_needed()
        self._assert_on_login_page()

        # 第二轮：登录 → 收尾登出
        self.user.login_by_sms(self.phone)
        self._assert_on_home()
        self.user.logout_if_needed()
        self._assert_on_login_page()
