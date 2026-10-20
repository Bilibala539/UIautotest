# CASE-ID: player-POS-019
"""Swan 回归·播放器：切歌原子重建与代次递增表现（player-POS-019）。

步骤 → AW 映射：
- 前置 播放中 → preset_playing("speaker") + open_player_page()
- 步骤1 记录曲名 A 与进度值 → read_player_title() + read_player_progress()
- 步骤2 点击下一首切换至曲目 B → player_control("next")（下一首 [图] 点击，
  内部断言切后播放态；trackGen 递增的原子重建不外显残影）
- 步骤2/3 断言重建 → read_player_title() 曲名变化（曲名变 B）+ assert_playing()
  （切歌后自动续播，无空白闪断）+ read_player_progress()（进度重置后可读）

原子重建回归面：身份/进度同步更新，播放连续，lastReady 残影不外显。
（歌词重载为歌词域面，本包 queue/lyric 页未解锁不展开——见 report 注记。）
清理：停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestTrackSwitchAtomicRebuild(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """切歌原子重建与代次递增表现（POS-019）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_track_switch_atomic_rebuild(self):
        """记录曲名 A → 下一首切至 B → 曲名变化且自动续播。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1：记录曲名 A 与进度值
        title_a = self.userA.read_player_title()
        assert title_a, "起播后读不到曲名 A（Ready 相位未确立）"
        before = self.userA.read_player_progress()
        assert before is not None, "读不到曲目 A 进度双时间"
        # 步骤2：点击下一首（原子重建，曲名变 B）
        self.userA.player_control("next")
        # 步骤2/3：重建断言——曲名变化 + 自动续播 + 进度重置可读
        title_b = self.userA.read_player_title()
        assert title_b, "切歌后读不到曲名 B（重建未完成/空白窗口）"
        assert title_b != title_a, (
            f"切歌后曲名未变化：A={title_a!r} B={title_b!r}（原子重建未触发？）")
        self.userA.assert_playing()
        after = self.userA.read_player_progress()
        assert after is not None, "切歌后读不到进度双时间（进度未重置？）"
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
