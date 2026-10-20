# CASE-ID: player-NEG-034
"""Swan 回归·播放器：冷启动立即开播放页零 ANR（player-NEG-034）。

⚠️ 部分转换：步骤2「hierarchy 可达性检查」与步骤3 探针登记语义（两次复现
才记候选、登记不提单）为平台侧执行门禁职责，不纳入 UI 脚本；本脚本覆盖
步骤1 冷启动立即点底栏开全屏页的 ANR 负向断言。

步骤 → AW 映射：
- 前置 持久播放会话 → preset_playing("speaker")（会话持久化，relaunch 不清，
  冷启动后底栏迷你播放器有恢复会话可点）
- 步骤1 冷启动 → restart_app()；立即点击底栏迷你播放器 → click_bottom_player_bar()
  （透明路由叠层时点：冷启动窗口期直接点条，底部滑入转场不构成启动期阻塞）
- 全屏页打开断言 → click_bottom_player_bar 内部页锚等待 + open_player_page() 幂等确保
- 播放会话恢复断言 → assert_playing()
- ANR 负向断言 → text_not_exists("responding")（「Swan Audio isn't responding」
  对话框文案 OCR 不可见）
清理：无（只读探针；teardown pass）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestColdStartOpenPlayerNoAnr(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """冷启动立即开播放页零 ANR（NEG-034）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_open_player_no_anr(self):
        """冷启动立即点底栏开全屏播放页：无 ANR、页面可达、播放恢复。"""
        self.userA.preset_playing("speaker")
        # 步骤1：冷启动后立即点击底栏迷你播放器（启动时序 ANR 类探针时点）
        self.userA.restart_app()
        self.userA.click_bottom_player_bar()
        # 全屏播放页打开（页锚等待在 click_bottom_player_bar 内，此处幂等确保）
        self.userA.open_player_page()
        # 播放会话恢复 + ANR 负向断言
        self.userA.assert_playing()
        self.userA.text_not_exists("responding", timeout=3)

    def teardown(self) -> None:
        """无用例私有清理（只读探针，会话随冷启动模型回收）。"""
        pass
