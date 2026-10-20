# CASE-ID: login-POS-012
"""Swan 回归·会话与登录:验证码满四位自动提交成功登录(login-POS-012)。

步骤→AW 映射:
1. 进入验证码输入页(真实发码,enter_sms_code_step) → 网关取码
   (otp.get_code,真实码);
2. 分段填入:先 3 位(fill_sms_code 追加语义) → 不自动提交:未进首页
   (assert_not_on_home)、仍在输码页(输入框 [图] 命中);
3. 补第 4 位 → 满 4 位自动提交成功 → 进入已登录首页(assert_on_home)。
cleanup: 已登录态(登录成功);网关记录未消费,由 5 分钟时效自然过期;
   冷启动模型下后续用例按需自带登录前置。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestFourDigitAutoSubmit(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_four_digit_auto_submit(self) -> None:
        # 步骤 1:进入输码页并取真实码
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        record = self.userA.otp.get_code(self.userA.phone, wait=60)
        code = str(record.get("code", ""))
        assert len(code) == 4, f"网关验证码异常: {code!r}"
        # 步骤 2:先 3 位不自动提交
        self.userA.fill_sms_code(code[:3])
        self.userA.assert_not_on_home()
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=3) is not None, (
            "3 位即触发提交(应满 4 位才自动提交)")
        # 步骤 3:补第 4 位 → 自动提交成功进首页
        self.userA.fill_sms_code(code[3])
        self.userA.assert_on_home()
