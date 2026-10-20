# CASE-ID: profile-NEG-024
"""Swan 回归·M13 个人中心：绑定管理行条件显隐（profile-NEG-024）。

用例 → AW 映射（B 级条件转换）：
- 有「账号绑定管理」行（账号有第三方绑定态）：进入绑定页 → assert_page_not_blank
  → back 回个人信息页（第三方 SDK 容错为观察面，不可注入 → 执行注记）
- 无该行（无绑定态）：负向断言行不可见（显隐逻辑正确性）
清理（G3/G4）：只读/取消类操作；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg024BindingRowVisibility(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_binding_manage_row_visibility(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        if self.userA.find_text_by_ocr("账号绑定管理", timeout=3) is not None:
            self.userA.click_text("账号绑定管理")
            self.userA.assert_page_not_blank()
            self.userA.press_back()
            self.userA.assert_on_person_info(timeout=5)
        else:
            self.userA.text_not_exists("账号绑定管理", timeout=2)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
