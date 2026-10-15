"""Swan 回归·域1：未登录冷启动，断言落登录页（回归用例 1，状态条件用例）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域1）：
- 用例1 首次安装/未登录冷启动 → cold_start_assert(landed="login")
  ⚠️ 状态条件：需未登录态（135 常态已登录），未登录窗口未开时 skip

清理：冷启动后已停登录页——G3/G4 允许态，无需额外清理。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestColdStartLandsLogin(SwanLoginRegressionMixin, BaseTest):
    """未登录冷启动，断言落登录页（回归用例 1）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_lands_login(self):
        """用例1：未登录冷启动，断言落登录页（状态条件——需未登录态）。"""
        # 未登录态探测：登录页锚可见才跑（登出会消耗 135 会话恢复成本，
        # 本用例设计为"未登录窗口条件执行"）
        if not self.userA._login_page_anchor_visible(timeout=2) and \
                any(self.userA.probe_image(t, timeout=1) is not None
                    for t in self.userA._BOTTOM_NAV_TEMPLATES):
            pytest.skip(
                "账号当前已登录（首页壳锚可见）——用例1 需未登录态；"
                "登出属状态翻转操作，安排在未登录窗口执行")
        self.userA.cold_start_assert(landed="login")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
