"""Swan 回归·域1：登录后冷启动，断言落首页（回归用例 2）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域1）：
- 用例2 登录后冷启动 → cold_start_assert(landed="home")

清理：冷启动后已停首页——G3/G4 允许态，无需额外清理。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestColdStartLandsHome(SwanLoginRegressionMixin, BaseTest):
    """登录后冷启动，断言落首页（回归用例 2）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_lands_home(self):
        """用例2：登录后冷启动，断言落首页（全自动）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.cold_start_assert(landed="home")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
