# CASE-ID: profile-NEG-002
"""Swan 回归·M13 个人中心：我的 Tab 交互往返无 ANR（profile-NEG-002）。

用例 → AW 映射：
- 快速 Tab 往返（首页→平台→设备→我的）→ go_bottom_tab（内建到位断言）
- 顶卡进出个人资料页往返 → open_person_info + back_to_me_page
- 全程无 ANR 对话框 → assert_no_anr_dialog（OCR "isn't responding" 反向判据）
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg002TabRoundtripAnr(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_me_tab_roundtrip_no_anr(self) -> None:
        self.userA.open_me_page()
        # 快速 Tab 往返
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("平台")
        self.userA.go_bottom_tab("设备")
        self.userA.go_bottom_tab("我的")
        self.userA.assert_no_anr_dialog()
        # 顶卡 → 个人资料页 → 返回
        self.userA.open_person_info()
        self.userA.back_to_me_page()
        self.userA.assert_no_anr_dialog()

    def teardown(self) -> None:
        pass
