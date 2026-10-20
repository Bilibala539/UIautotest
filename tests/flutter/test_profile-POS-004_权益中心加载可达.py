# CASE-ID: profile-POS-004
"""Swan 回归·M13 个人中心：权益中心加载可达（profile-POS-004）。

用例 → AW 映射（B 级：AppBridge H5 页未探索）：
- 「权益中心」行进入 → open_rights_center（OCR 行 + assert_page_not_blank 兜底）
- back 返回我的页（收藏行 [图] 到位锚）
- H5 内容锚（权益商品/加载骨架）未探索 → 模板需求已登记（权益中心 H5 锚）
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos004RightsCenterReachable(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_rights_center_reachable(self) -> None:
        self.userA.open_me_page()
        self.userA.open_rights_center()
        self.userA.press_back()
        self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=15)

    def teardown(self) -> None:
        pass
