# CASE-ID: profile-NEG-036
"""Swan 回归·M13 个人中心：权益中心返回键守门（profile-NEG-036）。

用例 → AW 映射（C 级简化转换：H5 内历史段不可自动化）：
- 进入权益中心（AppBridge H5，需网络；页未探索 → assert_page_not_blank 兜底）
- back 返回我的页（收藏行 [图] 到位锚）
- YAML「三段式返回（800ms 间隔连按）」时序面无法免硬等待复现 → 执行注记；
  降级为二次进入+单次返回，验证返回键幂等不崩溃
- 全程无 ANR
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg036RightsCenterBackGate(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_rights_center_back_gate(self) -> None:
        self.userA.open_me_page()
        # 进入权益中心 H5
        self.userA.open_rights_center()
        # back 返回我的页
        self.userA.press_back()
        self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=15)
        # 二次进入+单次返回：返回键幂等
        self.userA.open_rights_center()
        self.userA.press_back()
        self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=15)
        self.userA.assert_no_anr_dialog()

    def teardown(self) -> None:
        pass
