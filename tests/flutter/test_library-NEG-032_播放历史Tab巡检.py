# CASE-ID: library-NEG-032
"""Swan 回归·M12 收藏与曲库：播放历史 Tab 巡检与清空入口约束（library-NEG-032）。

用例 → AW 映射：
- S1 六 Tab 遍历：open_home_card('最近播放') → 顶栏 [图] 锚 →
  visit_play_history_tabs()（分类 Tab 条 [图] 条带 region OCR 逐 Tab 去重
  点击巡检，Tab 文案不写死），断言至少点到一个 Tab。
- S2-S3 清空入口：assert_history_clear_entry_exists()（OCR「清空」存在性）；
  ⛔ 清空按钮不点击（禁"只执行不断言"+ 破坏性动作约束，禁区 9）——no-op
  现状断言降级为「入口存在 + 页壳数据不变（顶栏 [图] 仍在）」。
- 降级注记：S4 断网后查看缓存步不转（框架无断网/飞行模式手段，OTHER）。
清理：无数据变更（清空未执行），无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HISTORY_TOPBAR
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryNeg032HistoryTabsPatrol(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """播放历史六 Tab 巡检 + 清空入口存在性（不执行清空）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_tabs_patrol(self):
        """六个分类 Tab 可遍历点击，清空入口存在但不点击，页壳数据不变。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('最近播放')
        self.userA.image_exists(SWAN_HISTORY_TOPBAR, timeout=15)
        # S1：六 Tab 遍历（条带 OCR 巡检，Tab 文案不写死）
        self.userA.visit_play_history_tabs()
        # S2：清空入口存在性（不点击）
        self.userA.assert_history_clear_entry_exists()
        # S3：未执行清空，页壳数据不变
        self.userA.image_exists(SWAN_HISTORY_TOPBAR, timeout=5)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（清空未执行，无数据变更）。"""
        pass
