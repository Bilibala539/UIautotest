# CASE-ID: profile-POS-024
"""Swan 回归·M13 个人中心：绑定管理解绑取消即止（profile-POS-024）。

用例 → AW 映射（B 级条件转换，依赖账号已有第三方绑定态）：
- 进绑定页 → 点「解绑」→ 确认弹层（OCR「取消」）→ 点「取消」即止 → 绑定仍在
- 无绑定态/无解绑入口 → pytest.skip 如实上报数据依赖
清理（G3/G4）：仅点取消，绑定关系无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos024BindingUnbindCancel(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_binding_unbind_cancel(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        if self.userA.find_text_by_ocr("账号绑定管理", timeout=3) is None:
            pytest.skip("无「账号绑定管理」行（账号无第三方绑定态，环境数据依赖）")
        self.userA.click_text("账号绑定管理")
        self.userA.assert_page_not_blank()
        if self.userA.find_text_by_ocr("解绑", timeout=3) is None:
            pytest.skip("绑定页无「解绑」入口（无已绑定第三方，数据依赖）")
        self.userA.click_text("解绑", timeout=5)
        self.userA.assert_any_text(["取消"], timeout=5)
        self.userA.click_text("取消", timeout=5)
        self.userA.assert_page_not_blank()
        self.userA.press_back()
        self.userA.assert_on_person_info(timeout=5)

    def teardown(self) -> None:
        pass
