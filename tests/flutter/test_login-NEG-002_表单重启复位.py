# CASE-ID: login-NEG-002
"""Swan 回归·会话与登录:进程重启后表单态不复现(login-NEG-002)。

步骤→AW 映射:
1. 密码形态构造错误面:ensure_password_form 切形态,填手机号+错误密码
   (密码框 [图] 点入)+勾协议,点「登录」提交 → [OCR] 已知错误文案
   「密码错误」命中,先锚定错误面成立;
2. 冷启动重启 → relaunch_app;断言落回登录页验证码形态(assert_sms_form):
   密码框 [图] 消失、「密码登入」[OCR] 入口重现、手机号不再回显。
注:错误密码用等价简单错误值(原数据含 shell 敏感符,不影响错误路径语义)。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PASSWORD_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestFormStateNotPersisted(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_form_state_not_persisted(self) -> None:
        # 步骤 1:密码形态构造错误面(手机号+错误密码+勾协议+提交)
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("Wr0ngPass2026")
        self.userA.press_back()  # 收软键盘
        self.userA.accept_agreement()
        self.userA.click_text("登录", timeout=10)
        assert self.userA.find_text_by_ocr("密码错误", timeout=15) is not None, (
            "错误密码提交后未见已知错误文案(错误面未成立,重启对照失真)")
        # 步骤 2:冷启动重启 → 表单态不复现
        self.userA.relaunch_app(self.userA.package)
        self.userA.assert_sms_form()
        assert self.userA.find_image(SWAN_PASSWORD_FIELD, timeout=2) is None, (
            "重启后密码框仍可见(表单形态被持久化)")
        assert self.userA.find_text_by_ocr("密码登入", timeout=5) is not None, (
            "重启后未落回默认验证码形态(缺「密码登入」入口)")
        assert self.userA.find_text_by_ocr(self.userA.phone, timeout=2) is None, (
            "重启后手机号仍回显(表单值被持久化)")
