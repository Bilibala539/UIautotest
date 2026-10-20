# CASE-ID: profile-POS-008
"""Swan 回归·M13 个人中心：音质弹层形态展示（profile-POS-008）。

用例 → AW 映射（A- 级）：
- 「音质设置」行 [图] 打开底部弹层 → open_quality_sheet
- 四档单选行渲染 → assert_quality_tiers（流畅/标准/HQ/SQ）
- 红字「完成」按钮 [图] 可见 → SWAN_SOUND_QUALITY_DONE_BUTTON
- 蒙层点击的免坐标等效替代：back 关闭（close_quality_sheet_by_back）
  → 我的页（收藏行 [图] 到位锚）
清理（G3/G4）：未提交选择即关闭；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos008QualitySheetShape(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_quality_sheet_shape(self) -> None:
        self.userA.open_me_page()
        self.userA.open_quality_sheet()
        self.userA.assert_quality_tiers()
        self.userA.image_exists("SWAN_SOUND_QUALITY_DONE_BUTTON", timeout=5)
        self.userA.close_quality_sheet_by_back()
        self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=5)

    def teardown(self) -> None:
        pass
