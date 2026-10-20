# CASE-ID: login-POS-021
"""Swan 回归·会话与登录:重发按钮冷却归零与倒计时重置(login-POS-021)。

步骤→AW 映射:
1. 验证码形态填号+勾协议+提交(真实发码 SMS #1) → 进入输码页(输入框 [图] 命中);
2. 首读倒计时命中(冷却中) → 轮询等待归零(wait_resend_ready,冷却 60s,
   禁固定 sleep,等待上限 90s);
3. 点「重新发送」(归零后可点态,[OCR] 无括号计数) → 仍在输码页
   (输入框 [图] 命中),倒计时重置(read_resend_countdown 重现且 >30);
4. 断言「验证码已经发送至」[OCR] 提示在(提示保持)。
注:真实发码 ×2;归零等待约 60s 为用例自身规定时长(YAML S2 等待上限 ≥60s);
   代理面请求计数为回填面,登记 report.notes。
cleanup: 网关记录未消费自然过期;真实短信 ×2,无遗留态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_ENABLED,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestResendCooldownReset(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_resend_cooldown_reset(self) -> None:
        # 步骤 1:发码进入输码页
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.accept_agreement()
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "提交后未进入验证码输入页")
        # 步骤 2:冷却中倒计时在屏,轮询至归零
        first = self.userA.read_resend_countdown(timeout=20)
        assert first is not None, "未读到重发倒计时(冷却未生效?)"
        self.userA.wait_resend_ready(timeout=90)
        # 步骤 3:归零后点重发 → 倒计时重置
        self.userA.click_text("重新发送", timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "点击重发后离开验证码输入页")
        reset = self.userA.read_resend_countdown(timeout=20)
        assert reset is not None and reset > 30, f"重发后倒计时未重置: {reset}"
        # 步骤 4:发送提示保持
        self.userA.text_exists("验证码已经发送至", timeout=10)
