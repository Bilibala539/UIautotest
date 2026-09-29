"""Swan 回归·收藏历史域：歌单收藏、歌曲收藏与最近播放（回归用例 41-68）。

用例 -> AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例41-43 歌单收藏（平台 × 收藏图标两态）-> favorite_playlist(platform, state)；
  两次 toggle 完成双向断言并回到初始态（收藏结果持久化在账号数据，
  不污染：无论初始态是收藏/未收藏，两次翻转后还原）
- 用例44-55 歌曲收藏到指定歌单 -> collect_song(target_platform, playlist,
  source)；source="player" 前置复用域3 start_play（经
  _preset_playing_on_favorite 到我喜欢页），source="playlist_page" 前置进
  收藏源歌单详情页（SOURCE_PLAYLIST，与目标歌单错开——run4c 实测同曲
  重复收藏会被 App 静默拦截，见 test_collect_song 注）；目标歌单默认
  rig 聚合歌单「我的音乐」（收藏结果无自动化回滚，见 SwanBusiness
  .collect_song 注记）
- 用例56-68 最近播放在历史页按分类出现 -> assert_recent_played(kind, name)
  （13条合1；歌曲类配置 SWAN_HISTORY_FRESH_PLAY=1 时现场播放造数据）

rig 环境变量见 swan_regression_common2.py 模块注释（本文件另有
SWAN_COLLECT_SOURCE_PLAYLIST，见 SOURCE_PLAYLIST 注）。
参数收集顺序（pytest 装饰器自下而上展开）：collect 用例 source="player"
先于 "playlist_page" 执行——player 用例先经播放页 [+] 完成一次成功收藏
（run4c 实测链路），playlist_page 用例随后从独立源歌单行内 [+] 收藏
（两参数各覆盖一个收藏入口，互不依赖对方数据）。
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

    # source="playlist_page" 用例的收藏源歌单（行内 [+] 所在详情页）：
    # 必须与目标歌单错开——目标歌单详情页任意行曲按定义已在目标歌单内，
    # 以其为源必触发 App「重复收藏」拦截（见 test_collect_song 注）。
    # 默认取 rig SWAN 宫格实测存在的「我的家庭」（5.3.2 探索样例歌单），
    # 数据约定：其顶行曲不得已在目标歌单内；rig 数据变化时用本变量覆盖。
    SOURCE_PLAYLIST = os.environ.get("SWAN_COLLECT_SOURCE_PLAYLIST", "我的家庭")

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

        数据设计（run4c 修正，run5 两次修正）：两参数须收藏不同歌曲到目标
        歌单——同曲重复收藏会触发 App「重复收藏」静默拦截（run4c run3 /
        run5 run1 双实测：宫格块点击后 toast「添加失败，请稍后重试」、停留
        「已选N首歌」页无跳转，收尾断言必炸）。
        - source="playlist_page"：源页从原目标歌单详情页改为独立源歌单
          SOURCE_PLAYLIST 详情页（其顶行曲按数据约定不在目标歌单内）；
        - source="player"（run5 改版）：不再收「播放全部首曲」（run5 实测
          首曲 Black White (AB) 已在目标歌单——run4c 该用例成功的收藏本身
          把曲送进了目标歌单，属一次性数据设计），改为点名播放
          COLLECT_PLAYER_SONG（SWAN_COLLECT_PLAYER_SONG 优先，回落
          SWAN_TEST_SONG）后收藏当前曲。
        - **数据态预校验（方案 C，run5 拍板）**：进收藏流程前先开目标歌单
          核对将收藏曲是否已在其中（playlist_has_song / playlist_top_song
          非断言探测），已在则 pytest.skip 带清晰理由——每轮诚实报数据态
          而非假红。耗尽时轮换手段（方案 A，运维口径）：换
          SWAN_COLLECT_SOURCE_PLAYLIST / SWAN_COLLECT_PLAYER_SONG，或由
          设备管理流程清理目标歌单（收藏结果无自动化回滚，行内垃圾桶
          红线禁点，见 collect_song 注）。
        source="player" 前置复用域3 start_play（经 _preset_playing_on_favorite
        到我喜欢页，收尾已在播放页）。"""
        self._ensure_logged_in_on_home()
        if source == "player":
            # 点名播放指定曲（不在目标歌单内的数据约定）；无配置回落
            # SWAN_TEST_SONG，二者皆空才走播放全部首曲（旧行为，无预校验——
            # 播放曲须开播后才可知，预校验不覆盖该遗留分支）
            song = self.COLLECT_PLAYER_SONG
            if song:
                self.user.open_playlist_detail(target_platform,
                                               self.COLLECT_PLAYLIST)
                if self.user.playlist_has_song(song):
                    pytest.skip(
                        f"数据态耗尽：{song!r} 已在目标歌单 "
                        f"{self.COLLECT_PLAYLIST!r}，请轮换 "
                        "SWAN_COLLECT_PLAYER_SONG 或清理目标歌单后重跑")
                self.user.back_to_tab_shell()
                self._preset_playing_on_favorite(source=song, mode="song")
            else:
                self._preset_playing_on_favorite()
        else:
            # 前置：源歌单详情页含 ≥1 首歌（SOURCE_PLAYLIST，与目标歌单
            # 错开的数据设计见本方法 docstring 与 SOURCE_PLAYLIST 注）
            self.user.open_playlist_detail("swan", self.SOURCE_PLAYLIST)
            source_song = self.user.playlist_top_song()
            self.user.back_to_tab_shell()
            self.user.open_playlist_detail(target_platform,
                                           self.COLLECT_PLAYLIST)
            if self.user.playlist_has_song(source_song):
                pytest.skip(
                    f"数据态耗尽：源顶行 {source_song!r} 已在目标歌单 "
                    f"{self.COLLECT_PLAYLIST!r}，请轮换 "
                    "SWAN_COLLECT_SOURCE_PLAYLIST 或清理目标歌单后重跑")
            self.user.back_to_tab_shell()
            self.user.open_playlist_detail("swan", self.SOURCE_PLAYLIST)
        self.user.collect_song(target_platform, self.COLLECT_PLAYLIST,
                               source=source)

    @pytest.mark.parametrize("kind,env_key", HISTORY_KINDS)
    def test_recent_played(self, kind, env_key):
        """用例56-68：最近播放按分类断言条目存在（条目名未配置则 skip）。

        歌曲类条件造数（run5 改版）：SWAN_HISTORY_FRESH_PLAY 配置时先探测
        目标曲是否已在最近播放可见（recent_played_visible），可见直接断言
        不造数；不可见才现场播放 3s 造记录（name 须为 rig 我喜欢歌单中的
        歌曲名）再断言——避免已有记录时的重复造数开销。
        """
        name = os.environ.get(env_key, "").strip()
        if not name:
            pytest.skip(f"未配置 {env_key}（rig 播放记录中的条目名）")
        if kind == "歌曲" and os.environ.get("SWAN_HISTORY_FRESH_PLAY", "").strip() \
                and not self.user.recent_played_visible(kind, name):
            # 现场播放造历史数据：点名播放 3s（确保最近播放落库，main
            # 拍板 3-5s 口径）即暂停（rig 卫生，避免音箱持续出声）
            self._preset_playing_on_favorite(source=name, mode="song")
            self.aw.sleep(3.0)
            self.user.player_control("pause")
        self.user.assert_recent_played(kind, name)
