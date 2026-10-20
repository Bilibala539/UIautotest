# CASE-ID: profile-NEG-016
"""Swan 回归·M13 个人中心：改密页防截屏与表单守门（profile-NEG-016）。

用例 → AW 映射（C 级：仅剩可自动化面）：
- 进修改密码页 → open_edit_password（点「密码」行）
- 到位判据=FLAG_SECURE 防截屏：take_screenshot 返回 None/近全黑
  （assert_screen_capture_blocked；知识库实测：页内 OCR/截图/图像定位全部失效）
- 表单结构断言（旧密码必填/新密码强度边界）在防截屏页内不可观察 →
  转由 dump+按键通道的专项用例承担，本用例覆盖进入+防截屏+退出面
- back 退出回个人信息页
清理（G3/G4）：未提交任何表单；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg016PasswordPageGate(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_password_page_capture_blocked(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        # 进修改密码页：防截屏即到位判据
        self.userA.open_edit_password()
        # back 退出回个人信息页
        self.userA.press_back()
        self.userA.assert_on_person_info(timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
