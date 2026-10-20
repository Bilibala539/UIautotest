# CASE-ID: player-NEG-025
"""Swan 回归·播放器：切后台挂起回落 pause 不自动恢复（player-NEG-025）。

步骤 → AW 映射：
- 步骤1 本机起播并记录进度 → preset_playing("speaker") + read_player_progress()
  （OCR 双时间可读=进度推进佐证，assert_playing 已含封面动检双证据）
- 步骤2 切后台 30s → background_resume(expect_image=SWAN_PLAYER_PROGRESS_BAR,
  back_seconds=30)（home 键切后台→停留→拉回前台；恢复锚=进度条 [图]，
  播/停两态恒在）
- 步骤3 回前台断言恢复语义 → assert_paused()（挂起回落暂停，不越权自动恢复）
- 步骤4 用户手动恢复 → player_control("play") + assert_playing() +
  read_player_progress()（进度从挂起点续走，无跳变）

生命周期边界回归面：后台/音频焦点不在会话层越权，回前台保持 paused 待用户操作。
清理：显式停止播放 → player_control("pause")（计时收尾）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYER_PROGRESS_BAR
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestBackgroundSuspendFallsBackPaused(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """切后台挂起回落 pause 不自动恢复（NEG-025）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_background_suspend_falls_back_paused(self):
        """本机起播 → 后台 30s → 回前台保持 paused → 手动恢复进度续走。"""
        self.userA.preset_playing("speaker")
        # 步骤1：记录进度（OCR 双时间可读）
        before = self.userA.read_player_progress()
        assert before is not None, "起播后 OCR 读不到进度双时间（进度条锚失配？）"
        # 步骤2：home 切后台 30s 后拉回前台（恢复锚=进度条 [图]，两态恒在）
        self.userA.background_resume(expect_image=SWAN_PLAYER_PROGRESS_BAR,
                                     back_seconds=30)
        # 步骤3：挂起回落暂停，不越权自动恢复
        self.userA.assert_paused()
        # 步骤4：用户手动恢复，播放态恢复、进度从挂起点续走
        self.userA.player_control("play")
        self.userA.assert_playing()
        after = self.userA.read_player_progress()
        assert after is not None, "手动恢复后 OCR 读不到进度双时间"
        assert after[0] >= before[0] - 5, (
            f"进度回跳：挂起前已播 {before[0]}s，恢复后仅 {after[0]}s（越权清零？）")
        # 清理：显式停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放，会话随冷启动模型回收）。"""
        pass
