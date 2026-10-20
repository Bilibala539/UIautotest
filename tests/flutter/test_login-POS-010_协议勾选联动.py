# CASE-ID: login-POS-010
"""Swan 回归·会话与登录:协议勾选状态跨形态联动翻转(login-POS-010)。

步骤→AW 映射:
1. 验证码形态填号(协议未勾) → 主按钮置灰(assert_sms_submit_enabled(False));
2. 勾协议(accept_agreement) → 启用(assert_sms_submit_enabled(True));
3. 切密码形态填密码(协议态跨形态保留) → 密码步主按钮启用;
4. 密码页取消勾选(cancel_agreement) → 密码步主按钮回置灰(联动翻转)。
注:第三方图标(微信/微博)可见性为模板回填面,登记 report.template_needs;
   本条不提交表单,零短信成本。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PASSWORD_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestAgreementToggleLinkage(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_agreement_toggle_linkage(self) -> None:
        # 步骤 1-2:验证码形态勾选联动
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.assert_sms_submit_enabled(False)
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 3:切密码形态,协议态保留 + 三要素齐 → 启用
        self.userA.ensure_password_form()
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SwanTest123")
        self.userA.press_back()  # 收软键盘
        self.userA.assert_password_submit_enabled(True)
        # 步骤 4:密码页取消勾选 → 联动回置灰
        self.userA.cancel_agreement()
        self.userA.assert_password_submit_enabled(False)
