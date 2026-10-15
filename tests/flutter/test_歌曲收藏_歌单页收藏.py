"""Swan 回归·收藏历史域：歌曲收藏到指定歌单（回归用例 44-55）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域7）：
- 用例44-55 歌曲收藏到指定歌单 → collect_song(target_platform, playlist,
  source)；source="player" 前置复用域3 start_play（经
  _preset_playing_on_favorite 到我喜欢页），source="playlist_page" 前置进
  收藏源歌单详情页（SOURCE_PLAYLIST）；目标歌单默认 rig 聚合歌单
  「我的音乐」。

可重复性（run6 设计，run4c/run5 双实测同曲重复收藏会被 App「添加失败，
请稍后重试」静默拦截）：两分支收藏前均先把目标曲从目标歌单经行内垃圾桶
移除（remove_song_from_playlist 预清理，测试清理语境可点的评估依据见该
方法 docstring）——playlist_page 分支先 top_song_row_name 提取源页最上行
歌名（与 _tap_song_row_plus 同锚定，提取行=将收藏行），player 分支直接用
COLLECT_PLAYER_SONG；预清理自愈往轮残留，任意歌可无限重复收藏，不再依赖
「曲不在目标歌单内」的一次性数据约定。

本文件另有 SWAN_COLLECT_SOURCE_PLAYLIST（见 SOURCE_PLAYLIST 注）；其余
rig 环境变量见 utils/aw/business/swan_regression.py 模块注释。
参数收集顺序（pytest 装饰器自下而上展开）：source="player" 先于
"playlist_page" 执行——player 用例先经播放页 [+] 完成一次成功收藏
（run4c 实测链路），playlist_page 用例随后从独立源歌单行内 [+] 收藏
（两参数各覆盖一个收藏入口，互不依赖对方数据）。
清理（G3/G4）：收播放页 → 退出 push 页 → go_home（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin



class TestCollectSong(SwanContentRegressionMixin, BaseTest):
    """歌曲收藏到指定歌单（回归用例 44-55）。"""

    # source="playlist_page" 用例的收藏源歌单（行内 [+] 所在详情页）：
    # 须含 ≥1 首歌（其顶行曲将被收藏）；rig 数据变化时用环境变量覆盖
    SOURCE_PLAYLIST = os.environ.get("SWAN_COLLECT_SOURCE_PLAYLIST", "我的家庭")

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_collect_song(self):
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
        self.userA.ensure_logged_in_on_home()
        # 前置：源歌单详情页含 ≥1 首歌（SOURCE_PLAYLIST）；行内 [+] 恒收
        # 最上行——先提取最上行歌名，把它从目标歌单移除（若在）再重进
        self.userA.open_playlist_detail("swan", self.SOURCE_PLAYLIST)
        source_song = self.userA.top_song_row_name()
        self.userA.remove_song_from_playlist(
            'swan', self.COLLECT_PLAYLIST, source_song)
        # remove 后置条件=tab 壳（open_playlist_detail 对任意歌单详情页
        # 短路，须壳态起点防同页短路误路由），重进源页进入收藏
        self.userA.open_playlist_detail("swan", self.SOURCE_PLAYLIST)
        self.userA.collect_song('swan', self.COLLECT_PLAYLIST,
                               source='playlist_page')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
