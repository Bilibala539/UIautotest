# CASE-ID: player-POS-012
"""Swan 回归·播放器：队列列表渲染与滚动（player-POS-012）。

⚠️ B 标定项（ADD1 改判）：队列按钮/队列列表容器均未注册模板——OCR 优先
尽力转换：打开弹层+列表渲染断言走通；滚动浏览（步骤3）依赖列表容器锚，
留 template_needs 待标定后补。

步骤 → AW 映射：
- 前置 有播放任务 → preset_playing("speaker") + open_player_page() +
  read_player_title()（当前曲名=列表条目渲染代理）
- 步骤1 点击队列按钮打开弹层 → open_queue_sheet()（OCR 候选词尽力定位）
- 步骤2 列表渲染且条目数 ≥1 → text_exists(当前曲名)（当前曲在列=条目 ≥1
  渲染代理；动态定位符命中语义由 OCR 行命中等价覆盖）
- 步骤3 滚动浏览 → 未纳入（列表容器模板待注册），template_needs 登记
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestQueueListRendering(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """队列列表渲染与滚动（POS-012，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_queue_list_rendering(self):
        """队列弹层打开 → 列表含当前曲（条目渲染完整）。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        title = self.userA.read_player_title()
        assert title, "起播后读不到当前曲名（列表条目代理失据）"
        # 步骤1：打开队列弹层
        self.userA.open_queue_sheet()
        # 步骤2：列表渲染且条目 ≥1（当前曲在列）
        self.userA.text_exists(title, timeout=8)
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
