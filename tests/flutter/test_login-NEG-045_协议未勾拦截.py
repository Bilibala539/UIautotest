# CASE-ID: login-NEG-045
"""Swan 回归·会话与登录:协议未勾选三入口拦截与恢复(login-NEG-045)。

步骤→AW 映射:
1. 验证码形态填合法 11 位(协议未勾) → 主按钮置灰(assert_sms_submit_enabled
   (False));点置灰主按钮(SWAN_LOGIN_SUBMIT_BTN [图]) → 吸收:未进输码页
   (输入框 [图] 不可见)、仍验证码形态(assert_sms_form);
2. 切密码形态 → 置灰点「登录」 → 吸收:仍密码形态且无「密码错误」[OCR];
3. 补齐门控(填密码+勾协议) → 密码步主按钮恢复启用
   (assert_password_submit_enabled(True));回切验证码形态主按钮亦启用。
注:第三方图标(微信/微博)可见性为模板回填面,登记 report.template_needs;
   全程未触发发码,零短信成本。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_BTN,
    SWAN_PASSWORD_FIELD,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestAgreementUncheckedBlock(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_agreement_unchecked_block(self) -> None:
        # 步骤 1:验证码形态置灰主按钮吸收
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.assert_sms_submit_enabled(False)
        self.userA.click_image(SWAN_LOGIN_SUBMIT_BTN, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=3) is None, (
            "协议未勾点置灰主按钮仍进入输码页(门控失效)")
        self.userA.assert_sms_form()
        # 步骤 2:密码形态置灰「登录」吸收
        self.userA.ensure_password_form()
        self.userA.assert_password_submit_enabled(False)
        self.userA.click_text("登录", timeout=10)
        self.userA.assert_password_form()
        self.userA.text_not_exists("密码错误", timeout=3)
        # 步骤 3:补齐门控 → 两形态主按钮恢复启用
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SwanTest123")
        self.userA.press_back()  # 收软键盘
        self.userA.accept_agreement()
        self.userA.assert_password_submit_enabled(True)
        self.userA.click_text("验证码登入", timeout=10)
        self.userA.assert_sms_submit_enabled(True)
