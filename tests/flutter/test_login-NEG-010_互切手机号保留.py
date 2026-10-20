# CASE-ID: login-NEG-010
"""Swan 回归·会话与登录:登录/密码形态互切 手机号保留(login-NEG-010)。

步骤→AW 映射:
1. 验证码形态填 11 位手机号+勾协议(fill_phone_number + accept_agreement);
2. 切密码形态(ensure_password_form) → [OCR] 手机号仍页内命中(形态切换不清号码);
3. 密码形态填入密码后回切验证码形态(点「验证码登入」)再切回密码形态
   (ensure_password_form 幂等) → 手机号仍命中(跨双切换保留)。
注:密码掩码值保留为回填面(掩码圆点不可 OCR 观测),登记 report.notes;
   协议态跨形态保留探针亦为记录面,不落断言。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PASSWORD_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestModeSwitchKeepsPhone(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_mode_switch_keeps_phone(self) -> None:
        # 步骤 1:验证码形态填号+勾协议
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.accept_agreement()
        # 步骤 2:切密码形态 → 手机号保留
        self.userA.ensure_password_form()
        assert self.userA.find_text_by_ocr(self.userA.phone, timeout=5) is not None, (
            "切到密码形态后手机号被清空")
        # 步骤 3:填密码 → 回切验证码形态 → 再切回密码形态 → 手机号仍保留
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SwanTest123")
        self.userA.press_back()  # 收软键盘
        self.userA.click_text("验证码登入", timeout=10)
        self.userA.ensure_password_form()
        assert self.userA.find_text_by_ocr(self.userA.phone, timeout=5) is not None, (
            "跨双形态切换后手机号被清空")
