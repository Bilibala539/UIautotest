# CASE-ID: launch-POS-013
"""Swan 回归·M01 启动与隐私：登出返回键不可达已登录主页（launch-POS-013）。

用例 → AW 映射：
- 已登录态 → ensure_logged_in_on_home()（登录态保障，幂等）
- 我的页登出 → logout_if_needed()（内部按需登出并落登录页）
- 返回键不可达已登录主页 → press_back() + assert_on_login_page()（仍在登录页）
平台目录缓存重置（PlatformCatalog.reset）为登出内部机制，UI 面不可
观测，不在脚本内表达。
清理（YAML cleanup）：teardown 重新登录恢复登录态，供后续用例衔接。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchPos013LogoutStackClear(SwanRP01Mixin, BaseTest):
    """登出返回键不可达已登录主页（launch-POS-013）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_back_after_logout_stays_on_login(self):
        """登出落登录页后按返回键，应仍停留在登录页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.logout_if_needed()
        self.userA.assert_on_login_page()
        self.userA.press_back()
        self.userA.assert_on_login_page()

    def teardown(self) -> None:
        """用例私有清理（YAML cleanup）：重新登录恢复登录态。"""
        self.userA.login()
