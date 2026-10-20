# CASE-ID: profile-NEG-004
"""Swan 回归·M13 个人中心：手机号明文展示且只读（profile-NEG-004）。

用例 → AW 映射：
- 我的页顶卡明文手机号 → text_exists(userA.phone)（运行时账号值，非硬编码）
- 个人资料页手机号行一致 → open_person_info + text_exists(userA.phone)
- 点击手机号行无跳转 → click_text(userA.phone) 后仍在资料页（assert_on_person_info）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg004PhonePlaintextReadonly(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_phone_plaintext_readonly(self) -> None:
        self.userA.open_me_page()
        # 顶卡明文手机号
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 个人资料页手机号行
        self.userA.open_person_info()
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 点击手机号行：不可点击，应无跳转
        self.userA.click_text(self.userA.phone, timeout=5)
        self.userA.assert_on_person_info(timeout=5)
        self.userA.back_to_me_page()
        self.userA.text_exists(self.userA.phone, timeout=5)

    def teardown(self) -> None:
        pass
