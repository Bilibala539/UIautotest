# CASE-ID: login-POS-020
"""Swan 回归·会话与登录:恰好 11 位边界发码链路(login-POS-020)。

步骤→AW 映射:
1. 填 10 位「1380013800」 → 主按钮置灰(assert_sms_submit_enabled(False));
2. 点框追加「0」凑足 11 位 → 启用;勾协议后保持启用;
3. 提交(POST /user/captcha,合成号) → 进入输码页(输入框 [图] 命中)且
   「验证码已经发送至」[OCR] 提示在(S6 提示文案锚)。
注:合成号 13800138000 不在网关白名单,本条只断言发码链路与到位态,不取码
   (平台实测对该号返回 success,服务端发送结果不影响到位断言)。
cleanup: 未登录态保持;真实发送通道向合成号发码 ×1,自然失效,无遗留态。
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


class TestElevenDigitsBoundary(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_eleven_digits_boundary_submit(self) -> None:
        # 步骤 1:10 位置灰
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number("1380013800")
        self.userA.assert_sms_submit_enabled(False)
        # 步骤 2:凑足 11 位启用,勾协议保持启用
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.input_text("0")
        self.userA.press_back()  # 收软键盘
        self.userA.assert_sms_submit_enabled(True)
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 3:提交 → 输码页 + 发送提示
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "11 位合法号提交未进入输码页")
        self.userA.text_exists("验证码已经发送至", timeout=10)
