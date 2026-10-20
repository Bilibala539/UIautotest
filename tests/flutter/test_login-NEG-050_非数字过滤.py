# CASE-ID: login-NEG-050
"""Swan 回归·会话与登录:手机号非数字字符过滤(login-NEG-050)。

步骤→AW 映射:
1. 点手机号框输字母「abc」 → digitsOnly 过滤:[OCR] 页内无「abc」回显;
2. 续输数字「135」 → [OCR]「135」回显(数字保留),3 位主按钮置灰;
3. 续输 8 位凑足 11 位「13555555555」 → 主按钮启用(assert_sms_submit_enabled(True))。
注:全角数字探针为记录面(adb 输入通道对全角字符支持不定),不落本脚本;
   全程不点击提交,零短信成本。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_PHONE_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestNonDigitFiltered(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_non_digit_filtered(self) -> None:
        # 步骤 1:字母被过滤
        self.userA.ensure_fresh_sms_form()
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("abc")
        assert self.userA.find_text_by_ocr("abc", timeout=3) is None, (
            "字母未被过滤仍回显在手机号框")
        # 步骤 2:数字保留,3 位置灰
        self.userA.input_text("135")
        self.userA.press_back()  # 收软键盘
        assert self.userA.find_text_by_ocr("135", timeout=5) is not None, (
            "过滤字母后数字未保留")
        self.userA.assert_sms_submit_enabled(False)
        # 步骤 3:凑足 11 位 → 启用
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.input_text("55555555")
        self.userA.press_back()  # 收软键盘
        self.userA.assert_sms_submit_enabled(True)
