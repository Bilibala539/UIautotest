"""Swan 回归·收藏历史域：歌单收藏开关（回归用例 41-43）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例41-43 歌单收藏（平台 × 收藏图标两态）→ favorite_playlist(platform, state)；
  两次 toggle 完成双向断言并回到初始态（收藏结果持久化在账号数据，
  不污染：无论初始态是收藏/未收藏，两次翻转后还原）

平台列表经 SWAN_FAV_PLATFORMS 注入（默认 swan；第三方平台须授权态，
见方案 §5⑤）。rig 环境变量与公共前置/清理见
utils/aw/business/swan_regression.py。
清理（G3/G4）：收播放页 → 退出 push 页 → go_home（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestFavoritePlaylistToggle(SwanContentRegressionMixin, BaseTest):
    """歌单收藏开关（回归用例 41-43）。"""

    @pytest.mark.parametrize("platform",
                             SwanContentRegressionMixin.FAVORITE_PLATFORMS)
    def test_favorite_playlist_toggle_twice(self, platform):
        """用例41-43：歌单收藏图标两态 [图] 双向断言，两次 toggle 回滚初始态。"""
        self._ensure_logged_in_on_home()
        self.user.favorite_playlist(platform, state="toggle")
        self.user.favorite_playlist(platform, state="toggle")  # 翻回初始态（回滚）
