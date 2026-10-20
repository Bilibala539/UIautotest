# CASE-ID: login-POS-002
"""Swan 回归·会话与登录:密码登录形态契约与三要素门控(login-POS-002)。

步骤→AW 映射:
1. 切密码形态(ensure_password_form) → 形态契约断言:手机号框 [图]、密码框 [图]
   (右侧闭眼图标入模)、协议未选态 [图]、回切钮「验证码登入」[OCR]、
   提交钮「登录」[OCR]、区号「+86」[OCR]、占位「请输入手机号」/「请输入密码」[OCR];
2. 门控①:仅填手机号 → 密码步主按钮仍置灰(assert_password_submit_enabled(False));
3. 门控②:补密码(协议未勾) → 仍置灰;
4. 门控③:勾协议 → 主按钮启用(assert_password_submit_enabled(True))。
注:本条不提交表单,零短信成本;闭眼/睁眼图标切换探针为记录面(仅闭眼图入模)。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_AGREEMENT_UNCHECKED,
    SWAN_LOGIN_PHONE_FIELD,
    SWAN_PASSWORD_FIELD,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestPasswordFormContract(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_password_form_contract(self) -> None:
        # 步骤 1:密码形态契约断言
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        assert self.userA.find_image(SWAN_LOGIN_PHONE_FIELD, timeout=5) is not None, (
            "密码形态缺手机号输入框")
        assert self.userA.find_image(SWAN_PASSWORD_FIELD, timeout=3) is not None, (
            "密码形态缺密码输入框")
        assert self.userA.find_image(SWAN_LOGIN_AGREEMENT_UNCHECKED, timeout=3) is not None, (
            "密码形态缺协议未选态勾选框")
        assert self.userA.find_text_by_ocr("验证码登入", timeout=3) is not None, (
            "密码形态缺「验证码登入」回切钮")
        assert self.userA.find_text_by_ocr("登录", timeout=3) is not None, (
            "密码形态缺「登录」提交钮")
        assert self.userA.find_text_by_ocr("+86", timeout=3) is not None, (
            "密码形态缺区号按钮")
        assert self.userA.find_text_by_ocr("请输入手机号", timeout=3) is not None, (
            "密码形态手机号占位文案缺失")
        assert self.userA.find_text_by_ocr("请输入密码", timeout=3) is not None, (
            "密码形态密码占位文案缺失")
        # 门控① 仅手机号 → 置灰
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.assert_password_submit_enabled(False)
        # 门控② 补密码(协议未勾) → 仍置灰
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SwanTest123")
        self.userA.press_back()  # 收软键盘
        self.userA.assert_password_submit_enabled(False)
        # 门控③ 勾协议 → 启用
        self.userA.accept_agreement()
        self.userA.assert_password_submit_enabled(True)
