"""Swan 回归·收藏历史域：歌单收藏、歌曲收藏与最近播放（回归用例 41-68）。

用例 -> AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例41-43 歌单收藏（平台 × 收藏图标两态）-> favorite_playlist(platform, state)；
  两次 toggle 完成双向断言并回到初始态（收藏结果持久化在账号数据，
  不污染：无论初始态是收藏/未收藏，两次翻转后还原）
- 用例44-55 歌曲收藏到指定歌单 -> collect_song(target_platform, playlist,
  source)；source="player" 前置复用域3 start_play（经
  _preset_playing_on_favorite 到我喜欢页），source="playlist_page" 前置经
  open_playlist_detail 进目标歌单详情页；目标歌单默认 rig 聚合歌单
  「我的音乐」（收藏结果无自动化回滚，见 SwanBusiness.collect_song 注记）
- 用例56-68 最近播放在历史页按分类出现 -> assert_recent_played(kind, name)
  （13条合1；歌曲类配置 SWAN_HISTORY_FRESH_PLAY=1 时现场播放造数据）

rig 环境变量见 swan_regression_common2.py 模块注释。
参数收集顺序（pytest 装饰器自下而上展开）：collect 用例 source="player"
先于 "playlist_page" 执行——player 用例先向目标歌单收藏 1 首，
playlist_page 用例随即有歌曲行可用（歌单初始为空时的自然造数顺序）。
清理（G3/G4）：teardown 收播放页 -> 退出 push 页 -> go_home。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from tests.flutter.swan_regression_common2 import SwanContentRegressionMixin

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

# (分类 kind, 条目名环境变量)；歌曲类条目名复用播放器域 SWAN_TEST_SONG
HISTORY_KINDS = [
    ("歌曲", "SWAN_TEST_SONG"),
    ("歌单", "SWAN_HISTORY_PLAYLIST"),
    ("歌手", "SWAN_HISTORY_ARTIST"),
    ("专辑", "SWAN_HISTORY_ALBUM"),
    ("电台", "SWAN_HISTORY_RADIO"),
    ("播客", "SWAN_HISTORY_PODCAST"),
]


class TestPlaylistFavoriteAndHistory(SwanContentRegressionMixin, BaseTest):
    """歌单收藏、歌曲收藏与最近播放（回归用例 41-68）。"""

    @pytest.mark.parametrize("platform",
                             SwanContentRegressionMixin.FAVORITE_PLATFORMS)
    def test_favorite_playlist_toggle_twice(self, platform):
        """用例41-43：歌单收藏图标两态 [图] 双向断言，两次 toggle 回滚初始态。"""
        self._ensure_logged_in_on_home()
        self.user.favorite_playlist(platform, state="toggle")
        self.user.favorite_playlist(platform, state="toggle")  # 翻回初始态（回滚）

    @pytest.mark.parametrize("source", ["player", "playlist_page"])  # 内层按列表序：player 先跑
    @pytest.mark.parametrize("target_platform",
                             SwanContentRegressionMixin.COLLECT_PLATFORMS)
    def test_collect_song(self, target_platform, source):
        """用例44-55：歌曲收藏到目标歌单（来源 player/playlist_page × 目标平台）。

        同平台内 source="player" 先于 "playlist_page" 收集执行：player 用例
        先向目标歌单收藏 1 首，playlist_page 用例随即有歌曲行可用
        （歌单初始为空时的自然造数顺序）。"""
        self._ensure_logged_in_on_home()
        if source == "player":
            # 我喜欢页发起播放进播放页（域3 start_play 复用，收尾已在播放页）
            self._preset_playing_on_favorite()
        else:
            # 前置：目标歌单详情页含 ≥1 首歌（同批 source="player" 用例已收藏 1 首）
            self.user.open_playlist_detail("swan", self.COLLECT_PLAYLIST)
        self.user.collect_song(target_platform, self.COLLECT_PLAYLIST,
                               source=source)

    @pytest.mark.parametrize("kind,env_key", HISTORY_KINDS)
    def test_recent_played(self, kind, env_key):
        """用例56-68：最近播放按分类断言条目存在（条目名未配置则 skip）。"""
        name = os.environ.get(env_key, "").strip()
        if not name:
            pytest.skip(f"未配置 {env_key}（rig 播放记录中的条目名）")
        if kind == "歌曲" and os.environ.get("SWAN_HISTORY_FRESH_PLAY", "").strip():
            # 现场播放造历史数据（name 须为 rig 我喜欢歌单中的歌曲名），
            # 断言前暂停（rig 卫生，避免音箱持续出声）
            self._preset_playing_on_favorite(source=name, mode="song")
            self.user.player_control("pause")
        self.user.assert_recent_played(kind, name)
