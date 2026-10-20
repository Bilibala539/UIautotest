# CASE-ID: login-NEG-051
"""Swan 回归·会话与登录:手机号分隔符过滤与 +86 前缀截断(login-NEG-051)。

步骤→AW 映射:
1. 填「135-5555-5555」 → 分隔符过滤为 11 位数字:[OCR]「13555555555」回显,
   主按钮启用;
2. 提交(合法号,真实发码) → 进入输码页(输入框 [图] 命中);
3. 冷启动重启回登录页,填「+8613555555555」 → 去前导+后 LengthLimiting 截断:
   [OCR]「86135555555」回显,主按钮启用(位数 11);
4. 提交 → 号段拦截(86 开头非法,零请求):未进输码页、仍验证码形态。
注:纯空格分隔变体为记录面(adb input text 空格转义不定,行为与 '-' 过滤同源);
   步骤 2 的遗留验证码未消费(未走网关取码,无 otp_id 可定位),5 分钟时效自然过期。
cleanup: 区号保持 +86;真实发码 ×1。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_PHONE_FIELD,
    SWAN_LOGIN_SUBMIT_ENABLED,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestPhoneFormatChars(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_phone_format_chars(self) -> None:
        # 步骤 1:'-' 分隔符过滤为 11 位
        self.userA.ensure_fresh_sms_form()
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("135-5555-5555")
        self.userA.press_back()  # 收软键盘
        assert self.userA.find_text_by_ocr("13555555555", timeout=5) is not None, (
            "分隔符未过滤或数字丢失")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 2:提交进入输码页(真实发码)
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "过滤后合法 11 位提交未进入输码页")
        # 步骤 3:重启后 +86 前缀去+截断
        self.userA.relaunch_app(self.userA.package)
        self.userA.assert_sms_form()
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("+8613555555555")
        self.userA.press_back()  # 收软键盘
        assert self.userA.find_text_by_ocr("86135555555", timeout=5) is not None, (
            "+86 前缀去+截断后回显不符")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 4:86 开头非法号段拦截
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is None, (
            "86 开头非法号段仍进入输码页(号段校验失效)")
        self.userA.assert_sms_form()
