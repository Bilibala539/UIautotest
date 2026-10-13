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

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestBackgroundResume(SwanLoginRegressionMixin, BaseTest):
    """后台恢复（回归用例 3）。"""

    def test_background_resume_home(self):
        """用例3：切后台再回前台，断言恢复到首页壳（全自动）。"""
        self._ensure_logged_in_on_home()
        self.user.background_resume()  # 默认锚=首页壳（底部导航 4 图）
