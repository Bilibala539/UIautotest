# CASE-ID: profile-NEG-026
"""Swan 回归·M13 个人中心：资料页危险区守门（profile-NEG-026）。

用例 → AW 映射（零点击设计：注销不可逆，绝不可误触）：
- 「退出登入」按钮 [图] 存在 → find_image(SWAN_PERSON_LOGOUT_BTN)
- 「注销账号」入口 OCR 存在 → find_text_by_ocr
- 布局守门：「注销账号」必须位于「退出登入」正上方（知识库实测相邻，防误点）
清理（G3/G4）：零点击只读断言；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg026DangerZoneGate(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_person_page_danger_zone_gate(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        # 「退出登入」按钮 [图] 与「注销账号」入口 OCR 均存在
        logout_pos = self.userA.find_image("SWAN_PERSON_LOGOUT_BTN", timeout=5)
        assert logout_pos is not None, "「退出登入」按钮 [图] 未定位到"
        danger = self.userA.find_text_by_ocr("注销账号", timeout=5)
        assert danger is not None, "「注销账号」入口未渲染"
        # 布局守门：注销入口在退出登入上方（危险区相邻布局）
        assert danger["cy"] < logout_pos[1], \
            "「注销账号」未位于「退出登入」上方（危险区布局漂移）"
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
