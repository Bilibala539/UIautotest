# CASE-ID: login-NEG-012
"""Swan 回归·会话与登录:港澳台区号提交门控分叉与 +86 对照(login-NEG-012)。

步骤→AW 映射:
1. +86 进区号页(open_area_page) → 点「中国香港」行(select_area_row)自动返回,
   断言区号按钮 [OCR]「+852」回填;
2. 填 11 位+勾协议 → 断言主按钮可用(assert_sms_submit_enabled(True)):
   港澳台段门控按位数(≥5 位)放行,11 位必启用(与 +86 号段门控分叉);
3. 对照组:从 +852 再进区号页 → 点中国整行(SWAN_AREA_CODE_CHINA_ROW [图])
   → 断言「+86」回填,同号主按钮仍启用(位数门控闭合)。
注:步骤 4「+852 下点下一步的服务端行为探针」为不确定性记录面,不落本脚本;
   本条全程不点击提交,零短信成本。
cleanup: 未登录态保持;区号已复位 +86(步骤 3),无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestHmtAreaCodeGating(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_hmt_area_code_gating(self) -> None:
        # 步骤 1:切到 +852(香港)
        self.userA.ensure_fresh_sms_form()
        self.userA.open_area_page("+86")
        self.userA.select_area_row("中国香港")
        assert self.userA.find_text_by_ocr("+852", timeout=5) is not None, (
            "选择中国香港后区号按钮未回填 +852")
        # 步骤 2:+852 下 11 位门控放行
        self.userA.fill_phone_number("13555555555")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 3:对照组——复位中国 +86,同号仍启用
        self.userA.open_area_page("+852")
        self.userA.select_china_area_row()
        assert self.userA.find_text_by_ocr("+86", timeout=5) is not None, (
            "选择中国行后区号按钮未回填 +86")
        self.userA.assert_sms_submit_enabled(True)
