# CASE-ID: profile-POS-027
"""Swan 回归·M13 个人中心：注销账号入口存在性（profile-POS-027）。

用例 → AW 映射（薄 A：零点击存在性断言）：
- 个人资料页「注销账号」入口 OCR 存在（注销位于退出登入正上方，布局见 NEG-026）
- 零点击：绝不进入注销流程（不可逆操作）
清理（G3/G4）：零点击只读断言；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos027CancelAccountEntryPresence(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_cancel_account_entry_presence(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        self.userA.text_exists("注销账号", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
