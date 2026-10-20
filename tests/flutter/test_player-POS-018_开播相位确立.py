# CASE-ID: player-POS-018
"""Swan 回归·播放器：开播相位确立（Switching→Ready 起播种子）（player-POS-018）。

步骤 → AW 映射：
- 步骤1 空闲会话点击曲目发起播放（RouteSelected→Switching，底栏过渡形态）
  → 冷启动模型保证空闲会话起点；preset_playing("speaker") 走完整开播链
  （我喜欢 → 播放全部 [图] → start_play 内部 _wait_player_page_open + assert_playing）
- 步骤2 等待媒体确认帧（MediaConfirmed，Ready 相位曲名渲染）→ read_player_title()
  （曲目区 OCR 非空）
- 步骤3 播放态与进度起点一致（T10 时间轴推进）→ assert_playing()（暂停键 [图]+
  封面动检双证据）+ read_player_progress()（进度从起点附近起走：已播 ≤30s）

开播全链回归面：曲名/播放态/进度三要素同步就位，无空白窗口。
清理：停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestPlayPhaseEstablishment(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """开播相位确立（POS-018）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_play_phase_establishment(self):
        """空闲会话起播 → 曲名渲染 → 播放态与进度起点一致。"""
        # 步骤1：空闲会话发起播放（冷启动模型保证起点无会话）
        self.userA.preset_playing("speaker")
        # 步骤2：Ready 相位曲名渲染（MediaConfirmed 后身份区就位）
        title = self.userA.read_player_title()
        assert title, "起播后曲目区 OCR 无曲名（Ready 相位未确立/渲染空白）"
        # 步骤3：播放态与进度起点一致（进度从起点附近起走）
        self.userA.assert_playing()
        progress = self.userA.read_player_progress()
        assert progress is not None, "起播后 OCR 读不到进度双时间"
        elapsed, total = progress
        assert elapsed <= 30, (
            f"起播进度未从起点附近起走：已播 {elapsed}s / 总 {total}s")
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
