# CASE-ID: login-NEG-048
"""Swan 回归·会话与登录:手机号 10/11/12 位边界门控与截断(login-NEG-048)。

步骤→AW 映射:
1. 填 10 位「1380013800」 → 主按钮置灰(assert_sms_submit_enabled(False));
2. 点框追加第 11 位「0」 → 凑足 11 位 → 主按钮启用(assert_sms_submit_enabled(True));
3. 清空重输 12 位「138001380001」 → LengthLimiting 截断为 11 位:
   [OCR] 回显「13800138000」、12 位串不回显,主按钮保持启用。
注:本条全程不点击提交(合成号不发码,零短信成本)。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_PHONE_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestPhoneDigitBounds(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_phone_digit_bounds(self) -> None:
        # 步骤 1:10 位 → 置灰
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number("1380013800")
        self.userA.assert_sms_submit_enabled(False)
        # 步骤 2:追加第 11 位 → 启用
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.input_text("0")
        self.userA.press_back()  # 收软键盘
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 3:12 位截断为 11 位
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("138001380001")
        self.userA.press_back()  # 收软键盘
        assert self.userA.find_text_by_ocr("13800138000", timeout=5) is not None, (
            "12 位输入截断后 11 位号码未回显")
        assert self.userA.find_text_by_ocr("138001380001", timeout=3) is None, (
            "12 位号码未被截断(LengthLimiting 失效)")
        self.userA.assert_sms_submit_enabled(True)
