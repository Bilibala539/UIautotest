# CASE-ID: player-POS-013
"""Swan 回归·播放器：队列当前曲目标记对齐（player-POS-013）。

⚠️ B 标定项（ADD1 改判）：队列按钮/当前标记 current_queue_current_marker
均未注册模板——OCR 优先尽力转换：打开弹层+当前曲行可见走通；标记唯一性
与贴顶对齐（步骤2/3）依赖标记模板，留 template_needs 待标定后补。

步骤 → AW 映射：
- 前置 播放队列中部曲目后打开弹层 → preset_playing("speaker")（播放全部
  首曲起播=队列有当前曲目）+ open_player_page() + read_player_title()
- 步骤1 打开队列弹层（视口内可见当前曲目标记）→ open_queue_sheet() +
  text_exists(当前曲名)（当前曲行在视口=标记可见的 OCR 等价代理）
- 步骤2/3 标记贴顶对齐/全列表唯一 → 未纳入（current_queue_current_marker
  模板待注册），template_needs 登记
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestQueueCurrentMarker(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """队列当前曲目标记对齐（POS-013，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_queue_current_marker(self):
        """打开队列弹层 → 当前曲行在视口（标记可见代理）。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        title = self.userA.read_player_title()
        assert title, "起播后读不到当前曲名（标记可见代理失据）"
        # 步骤1：打开队列弹层，当前曲目标记行在视口
        self.userA.open_queue_sheet()
        self.userA.text_exists(title, timeout=8)
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
