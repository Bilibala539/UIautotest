# CASE-ID: login-NEG-009
"""Swan 回归·会话与登录:密码形态返回键收软键盘停留(login-NEG-009 定案)。

步骤→AW 映射:
1. 短信形态切密码形态(ensure_password_form);
2. 点手机号输入框弹出软键盘(SWAN_LOGIN_PHONE_FIELD [图] 点入);
3. press_back 一次 → 定案为收软键盘并停留:断言仍处密码形态
   (assert_password_form:「验证码登入」[OCR] 在、「下一步」[OCR] 不在),
   且密码框 [图] 仍可见(页面未退)。
注:步骤 4「二次 back 行为探针」(回登录页 vs 退出)为不确定性记录面,不落本脚本。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_PHONE_FIELD,
    SWAN_PASSWORD_FIELD,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestPasswordPageBackKeyboard(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_password_page_back_collapses_keyboard(self) -> None:
        # 步骤 1-2:进密码形态并点手机号框弹软键盘
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        # 步骤 3:返回键收软键盘,停留密码形态
        self.userA.press_back()
        self.userA.assert_password_form()
        assert self.userA.find_image(SWAN_PASSWORD_FIELD, timeout=3) is not None, (
            "返回键后密码框不可见(页面被退出而非仅收键盘,与定案相悖)")
