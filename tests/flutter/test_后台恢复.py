# CASE-ID: aw-后台恢复
# LINKED-CASE: nav-POS-002,player-POS-022
"""Swan 回归·域1：后台恢复（回归用例 3）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域1）：
- 用例3 登录后热启动恢复 → background_resume()（默认首页壳锚）

清理：恢复后停在首页——G3/G4 允许态。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestBackgroundResume(SwanLoginRegressionMixin, BaseTest):
    """后台恢复（回归用例 3）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_background_resume_home(self):
        """用例3：切后台再回前台，断言恢复到首页壳（全自动）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.background_resume()  # 默认锚=首页壳（底部导航 4 图）

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
