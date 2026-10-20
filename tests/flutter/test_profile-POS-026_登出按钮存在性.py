# CASE-ID: profile-POS-026
"""Swan 回归·M13 个人中心：退出登入按钮存在性（profile-POS-026）。

用例 → AW 映射（薄 A：零点击存在性断言）：
- 个人资料页「退出登入」按钮 [图] 存在（SWAN_PERSON_LOGOUT_BTN 注册模板）
- 零点击：不触发登出流程（登出功能面由登录域用例承担）
清理（G3/G4）：零点击只读断言；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos026LogoutButtonPresence(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_logout_button_presence(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        self.userA.image_exists("SWAN_PERSON_LOGOUT_BTN", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
