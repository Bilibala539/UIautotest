# CASE-ID: login-NEG-052
"""Swan 回归·会话与登录:密码形态与短信步校验一致性(login-NEG-052)。

步骤→AW 映射:
1. 切密码形态,填 10 位「1380013800」+填密码+勾协议 → 主按钮置灰
   (assert_password_submit_enabled(False),位数门控与短信步一致);
2. 改输 11 位非法号段「12345678901」 → 主按钮启用(仅校验位数,与短信步一致);
3. 点「登录」 → 号段拦截(行内红字,与短信步一致):仍密码页
   (密码框 [图] 命中)且无「密码错误」[OCR](该文案属密码错误路径,不应出现)。
注:旧错误残留探针与密码值复测为回填面;行内红字拦截文案未截,
   登记 report.template_needs。全程不触发发码,零短信成本。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PASSWORD_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestCrossModeGatingConsistency(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_cross_mode_gating_consistency(self) -> None:
        # 步骤 1:密码形态 10 位 → 置灰
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        self.userA.fill_phone_number("1380013800")
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("SwanTest123")
        self.userA.press_back()  # 收软键盘
        self.userA.accept_agreement()
        self.userA.assert_password_submit_enabled(False)
        # 步骤 2:11 位非法号段 → 仅位数校验 → 启用
        self.userA.fill_phone_number("12345678901")
        self.userA.assert_password_submit_enabled(True)
        # 步骤 3:提交被号段拦截 → 停留密码页
        self.userA.click_text("登录", timeout=10)
        assert self.userA.find_image(SWAN_PASSWORD_FIELD, timeout=5) is not None, (
            "密码形态非法号段提交后离开密码页(与短信步校验不一致)")
        self.userA.text_not_exists("密码错误", timeout=3)
