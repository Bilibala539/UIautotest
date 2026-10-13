"""Swan 回归·域1：冷启动落页断言（回归用例 1-2）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域1）：
- 用例2 登录后冷启动 → cold_start_assert(landed="home")
- 用例1 首次安装/未登录冷启动 → cold_start_assert(landed="login")
  ⚠️ 状态条件：需未登录态（135 已登录），未登录窗口未开时 skip

清理：冷启动后已在首页（home 分支）/登录页（login 分支）——G3/G4 允许态。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestColdStartLandedPage(SwanLoginRegressionMixin, BaseTest):
    """冷启动落页断言（回归用例 1-2）。"""

    def test_cold_start_lands_home(self):
        """用例2：登录后冷启动，断言落首页（全自动）。"""
        self._ensure_logged_in_on_home()
        self.user.cold_start_assert(landed="home")

    def test_cold_start_lands_login(self):
        """用例1：未登录冷启动，断言落登录页（状态条件——需未登录态）。"""
        # 未登录态探测：登录页锚可见才跑（登出会消耗 135 会话恢复成本，
        # 本用例设计为"未登录窗口条件执行"）
        if not self.aw._login_page_anchor_visible(timeout=2) and \
                any(self._probe_image(t, timeout=1) is not None
                    for t in self._BOTTOM_NAV_TEMPLATES):
            pytest.skip(
                "账号当前已登录（首页壳锚可见）——用例1 需未登录态；"
                "登出属状态翻转操作，安排在未登录窗口执行")
        self.user.cold_start_assert(landed="login")
