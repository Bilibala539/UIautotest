# CASE-ID: login-NEG-030
"""Swan 回归·会话与登录:空手机号/空密码三象限提交吸收(login-NEG-030)。

步骤→AW 映射:
1. 密码形态全空直接点「登录」(click_text,按钮文案页内唯一) → 吸收:
   仍密码形态(assert_password_form)且无「密码错误」[OCR](text_not_exists);
2. 仅填手机号再点「登录」 → 吸收,断言同上;
3. 清空手机号、仅填密码再点「登录」 → 吸收,断言同上。
注:三象限均不产生网络提交,零短信成本;置灰态随行用
   assert_password_submit_enabled(False)(草稿图)辅助锚定。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_PHONE_FIELD,
    SWAN_PASSWORD_FIELD,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestEmptyPhonePasswordGating(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_empty_phone_password_gating(self) -> None:
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        # 象限 1:全空提交吸收
        self.userA.assert_password_submit_enabled(False)
        self.userA.click_text("登录", timeout=10)
        self.userA.assert_password_form()
        self.userA.text_not_exists("密码错误", timeout=3)
        # 象限 2:仅手机号提交吸收
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.assert_password_submit_enabled(False)
        self.userA.click_text("登录", timeout=10)
        self.userA.assert_password_form()
        self.userA.text_not_exists("密码错误", timeout=3)
        # 象限 3:清号仅填密码提交吸收
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SwanTest123")
        self.userA.press_back()  # 收软键盘
        self.userA.assert_password_submit_enabled(False)
        self.userA.click_text("登录", timeout=10)
        self.userA.assert_password_form()
        self.userA.text_not_exists("密码错误", timeout=3)
