# CASE-ID: home-POS-005
"""Swan 回归·首页：播放后最近播放乐观刷新(home-POS-005)。

步骤→AW 映射：
- 进首页推荐 → ensure_logged_in_on_home
- 进我喜欢歌单 → open_home_card('我喜欢')（含首页卡滚动定位与歌单页锚断言）
- 记录当前第一首歌名 → top_song_row_name()（OCR 首行歌名，运行时数据）
- 我喜欢页播放全部 → start_play('favorite', 'all')（进播放器页开播）
- 断言播放态 → assert_playing()
- 退回 Tab 壳层并回首页 → back_to_tab_shell() + go_home()
- 断言推荐页最近播放分组出现刚才播放的歌 → assert_recent_played('单曲', 歌名)
  （[OCR] 文本断言，YAML 预期"最近播放立即出现该歌曲"）

cleanup：无用例私有清理（播放态随下一次冷启动复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestRecentPlayedRefreshAfterPlay(SwanRP03Mixin, BaseTest):
    """前台播放我喜欢歌曲后，推荐页最近播放分组乐观刷新出该歌曲。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_recent_played_refresh_after_play(self):
        """播放我喜欢第一首歌 → 回首页 → 最近播放出现该歌。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('我喜欢')
        song = self.userA.top_song_row_name(timeout=10)

        self.userA.start_play('favorite', 'all')
        self.userA.assert_playing()
        self.userA.back_to_tab_shell()
        self.userA.go_home()

        self.userA.assert_recent_played('单曲', song)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在首页（播放态随冷启动复位）
