# CASE-ID: profile-POS-017
"""Swan 回归·M13 个人中心：手机号只读保护（profile-POS-017）。

用例 → AW 映射（A- 级）：
- 个人资料页手机号行明文展示 → text_exists(userA.phone)
- 点击手机号行无跳转（不可编辑，行不可点）→ assert_on_person_info
- 顶卡与资料页手机号一致 → 返回我的页后 text_exists(userA.phone)
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos017PhoneReadonly(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_phone_readonly_protection(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 点手机号行：无跳转
        self.userA.click_text(self.userA.phone, timeout=5)
        self.userA.assert_on_person_info(timeout=5)
        self.userA.back_to_me_page()
        self.userA.text_exists(self.userA.phone, timeout=5)

    def teardown(self) -> None:
        pass
