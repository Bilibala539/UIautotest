# CASE-ID: login-NEG-003
"""Swan 回归·会话与登录:已消费/过期验证码拒绝登录(login-NEG-003 分支 a·已消费)。

步骤→AW 映射:
1. 手机号步提交进入验证码输入页(真实发码,enter_sms_code_step);
2. 网关取最新验证码并先消费(OtpClient.get_code/consume)→ 再填入 4 位
   (fill_sms_code 追加语义,满 4 位自动提交);
3. 断言登录被拒:停留验证码输入页(输入框 [图] 仍在)且未进首页
   (assert_not_on_home 底部导航 4 图全不可见)。
cleanup: 未登录态保持;网关侧记录已被 consume 失效,无遗留可复用凭据。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestConsumedCodeRejected(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_consumed_code_rejected(self) -> None:
        # 步骤 1:进入验证码输入页(真实发码)
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        # 步骤 2:取码 → 先消费 → 再填入(自动提交)
        record = self.userA.otp.get_code(self.userA.phone, wait=60)
        code = str(record.get("code", ""))
        assert len(code) == 4, f"网关验证码异常: {code!r}"
        self.userA.otp.consume(record.get("id"))
        self.userA.fill_sms_code(code)
        # 步骤 3:已消费码被拒 → 停留输码页且未进首页
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "已消费验证码提交后未停留在验证码输入页")
        self.userA.assert_not_on_home()
