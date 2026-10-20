# CASE-ID: profile-POS-006
"""Swan 回归·M13 个人中心：SWAN收藏行进入（profile-POS-006）。

用例 → AW 映射（A- 级）：
- 「SWAN收藏」行进入（注意 UI 实际文案为「SWAN收藏」而非「我的收藏」，坑19 同源漂移）
  → open_favorites_page（OCR 行 + 分组行 [图] 兜底判据）
- back 返回我的页
清理（G3/G4）：浏览零点击；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos006FavoritesRowEntry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_favorites_row_entry(self) -> None:
        self.userA.open_me_page()
        self.userA.open_favorites_page()
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
