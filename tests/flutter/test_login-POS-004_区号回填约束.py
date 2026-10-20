# CASE-ID: login-POS-004
"""Swan 回归·会话与登录:港澳台区号回填与非 86 段约束(login-POS-004)。

步骤→AW 映射:
1. +86 进区号页 → 依次点选「中国香港」「中国澳门」「中国台湾」行
   (select_area_row,行文案 [OCR] 定位),每次自动返回断言区号回填
   +852/+853/+886([OCR]);
2. +852 下填 11 位+勾协议 → 主按钮启用(不截断,LengthLimiting 15,
   位数门控 ≥5 位放行,assert_sms_submit_enabled(True));
3. 收尾:+886 再进区号页 → 点中国整行([图])回 +86 → 填 16 位
   「1355555555512345」 → 截断 11 位([OCR]「13555555555」在,超长串不在)。
注:本条全程不提交,零短信成本;S2 机制探针(区号回填实现路径)为记录面。
cleanup: 区号复位 +86(步骤 3),未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_PHONE_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestAreaCodeBackfill(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_area_code_backfill(self) -> None:
        self.userA.ensure_fresh_sms_form()
        # 步骤 1:港/澳/台行回填
        self.userA.open_area_page("+86")
        self.userA.select_area_row("中国香港")
        assert self.userA.find_text_by_ocr("+852", timeout=5) is not None, (
            "中国香港行未回填 +852")
        self.userA.open_area_page("+852")
        self.userA.select_area_row("中国澳门")
        assert self.userA.find_text_by_ocr("+853", timeout=5) is not None, (
            "中国澳门行未回填 +853")
        self.userA.open_area_page("+853")
        self.userA.select_area_row("中国台湾")
        assert self.userA.find_text_by_ocr("+886", timeout=5) is not None, (
            "中国台湾行未回填 +886")
        # 步骤 2:+852 下 11 位不截断、门控放行
        self.userA.fill_phone_number("13555555555")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 3:复位 +86 + 16 位截断为 11 位
        self.userA.open_area_page("+886")
        self.userA.select_china_area_row()
        assert self.userA.find_text_by_ocr("+86", timeout=5) is not None, (
            "中国行未回填 +86")
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("1355555555512345")
        self.userA.press_back()  # 收软键盘
        assert self.userA.find_text_by_ocr("13555555555", timeout=5) is not None, (
            "16 位输入截断后 11 位号码未回显")
        assert self.userA.find_text_by_ocr("1355555555512", timeout=3) is None, (
            "16 位号码未被截断(LengthLimiting 15 失效)")
        self.userA.assert_sms_submit_enabled(True)
