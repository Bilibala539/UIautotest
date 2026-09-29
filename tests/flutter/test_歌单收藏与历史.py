"""Swan 回归·收藏历史域：歌单收藏、歌曲收藏与最近播放（回归用例 41-68）。

用例 -> AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例41-43 歌单收藏（平台 × 收藏图标两态）-> favorite_playlist(platform, state)；
  两次 toggle 完成双向断言并回到初始态（收藏结果持久化在账号数据，
  不污染：无论初始态是收藏/未收藏，两次翻转后还原）
- 用例44-55 歌曲收藏到指定歌单 -> collect_song(target_platform, playlist,
  source)；source="player" 前置复用域3 start_play（经
  _preset_playing_on_favorite 到我喜欢页），source="playlist_page" 前置进
  收藏源歌单详情页（SOURCE_PLAYLIST）；目标歌单默认 rig 聚合歌单
  「我的音乐」。可重复性（run6 设计，run4c/run5 双实测同曲重复收藏会被
  App「添加失败，请稍后重试」静默拦截）：两分支收藏前均先把目标曲从
  目标歌单经行内垃圾桶移除（remove_song_from_playlist 预清理，测试清理
  语境可点的评估依据见该方法 docstring）——playlist_page 分支先
  top_song_row_name 提取源页最上行歌名（与 _tap_song_row_plus 同锚定，
  提取行=将收藏行），player 分支直接用 COLLECT_PLAYER_SONG；预清理
  自愈往轮残留，任意歌可无限重复收藏，不再依赖「曲不在目标歌单内」的
  一次性数据约定
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
    # 默认取 rig SWAN 宫格实测存在的「我的家庭」（5.3.2 探索样例歌单）。
    # 数据约定（run6 起仅剩一条）：须含 ≥1 首歌（其顶行曲将被收藏）——
    # 旧「顶行曲不得已在目标歌单内」约定已由预清理运行时强制（收藏前先
    # 把顶行曲从目标歌单移除，见 test_collect_song 注），不再依赖 rig
    # 数据态；rig 数据变化（如该歌单被清空/改名）时用本变量覆盖。
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

        可重复性（run6 设计，取代 run5「预校验 skip + 人工轮换」方案 C）：
        同曲重复收藏会触发 App「重复收藏」静默拦截（run4c run3 / run5 run1
        双实测：宫格块点击后 toast「添加失败，请稍后重试」、停留「已选N首
        歌」页无跳转，收尾断言必炸）——两分支收藏前均先经
        remove_song_from_playlist 把目标曲从目标歌单经行内垃圾桶移除（测试
        清理语境可点，评估依据见该方法 docstring），自愈往轮收藏残留：任意
        歌可无限重复收藏，数据态耗尽不再 skip 而是当场清理后照常收藏。
        - source="player"：点名播放 COLLECT_PLAYER_SONG（SWAN_COLLECT_
          PLAYER_SONG 优先，回落 SWAN_TEST_SONG）后收藏当前曲；曲名已知，
          预清理先行再开播。二者皆空走播放全部首曲（旧行为，无预清理——
          播放曲须开播后才可知，预清理不覆盖该遗留分支）。
        - source="playlist_page"：源歌单 SOURCE_PLAYLIST 详情页行内 [+] 收藏
          （恒收最上行）——先 top_song_row_name 提取最上行歌名（与
          _tap_song_row_plus 同锚定，提取行=将收藏行），预清理后重进源页。
        source="player" 前置复用域3 start_play（经 _preset_playing_on_favorite
        到我喜欢页，收尾已在播放页）。"""
        self._ensure_logged_in_on_home()
        if source == "player":
            song = self.COLLECT_PLAYER_SONG
            if song:
                # 预清理（run6）：目标曲往轮收藏成功后仍留在目标歌单（收藏
                # 持久无自动回滚），先移除再开播，否则二轮必撞拦截（run5
                # 文件3 死因）
                self.user.remove_song_from_playlist(
                    target_platform, self.COLLECT_PLAYLIST, song)
                self._preset_playing_on_favorite(source=song, mode="song")
            else:
                self._preset_playing_on_favorite()
        else:
            # 前置：源歌单详情页含 ≥1 首歌（SOURCE_PLAYLIST）；行内 [+] 恒收
            # 最上行——先提取最上行歌名，把它从目标歌单移除（若在）再重进
            self.user.open_playlist_detail("swan", self.SOURCE_PLAYLIST)
            source_song = self.user.top_song_row_name()
            self.user.remove_song_from_playlist(
                target_platform, self.COLLECT_PLAYLIST, source_song)
            # remove 后置条件=tab 壳（open_playlist_detail 对任意歌单详情页
            # 短路，须壳态起点防同页短路误路由），重进源页进入收藏
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
