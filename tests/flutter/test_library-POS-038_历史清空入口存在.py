# CASE-ID: library-POS-038
"""Swan 回归·M12 收藏与曲库：播放历史清空入口存在性（library-POS-038）。

用例 → AW 映射：
- S1 进入播放历史：open_home_card('最近播放') → 顶栏 [图] 锚。
- S2 清空入口存在性：assert_history_clear_entry_exists()（OCR「清空」
  contains 口径）。
- ⛔ 清空按钮不点击（破坏性动作约束，禁区 9）——YAML 后续「点击清空+
  确认清空+核对数据态」段以「入口存在 + 页壳数据不变」收口，真实清空
  流程需专用隔离账号，登记 report.notes。
- S3 数据不变复核：image_exists(SWAN_HISTORY_TOPBAR)。
清理：清空未执行，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HISTORY_TOPBAR
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos038HistoryClearEntryExists(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """播放历史清空入口存在（不执行清空，页壳数据不变）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_clear_entry_exists(self):
        """清空入口存在且可断言，未执行清空，页壳保持。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('最近播放')
        # S1：页锚
        self.userA.image_exists(SWAN_HISTORY_TOPBAR, timeout=15)
        # S2：清空入口存在性（不点击）
        self.userA.assert_history_clear_entry_exists()
        # S3：数据不变复核
        self.userA.image_exists(SWAN_HISTORY_TOPBAR, timeout=5)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（清空未执行）。"""
        pass
