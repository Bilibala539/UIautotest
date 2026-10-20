# CASE-ID: login-POS-011
"""Swan 回归·会话与登录:重发倒计时递减/同号延续/改号重置(login-POS-011)。

步骤→AW 映射:
1. 验证码形态填号+勾协议+提交(真实发码) → 进入输码页(输入框 [图] 命中);
2. OCR 读重发按钮倒计时(read_resend_countdown,「重新发送(Ns)」):
   首读命中 N1(冷却中即重发不可点,S2 禁用态探针同步锚定) → 再读 N2 <
   N1(递减);
3. S3:页内返回箭头回手机号步(back_to_phone_step,NEG-005 定案通道) →
   不改号码再次提交(enter_sms_code_step 同号) → 直接切回验证码步 →
   read_resend_countdown 读 N3 ≤ N2:剩余时间延续(冷却内同号复用不发码;
   若重发则倒计时必重置 ~60 > N2,断言失败即暴露——S4「/captcha 请求
   计数=1」代理面的黑盒等价证据);
4. S5:再返回手机号步 → 改号 13900000003 提交(YAML 步骤明示合成号,
   POS-020 先例:合成号发码链路 success 可走,不取码) → 进验证码步 →
   read_resend_countdown 读 N4 ≥ 55 且 N4 > N3:改号发码倒计时重置 60。
注:S4 请求计数代理观察面由 S3 倒计时延续等价覆盖(report.notes 登记);
   本条真实/合成发码 ×2(主号 1 + 合成号 1,均在 YAML 步骤必要范围),不取码。
cleanup: 网关侧无记录(未取码),真实短信 ×2 自然过期,无遗留态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_ENABLED,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestResendCountdownDecreases(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_resend_countdown_decreases(self) -> None:
        # 步骤 1:发码进入输码页
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number(self.userA.phone)
        self.userA.accept_agreement()
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "提交后未进入验证码输入页")
        # 步骤 2:倒计时首读与二读,断言递减
        first = self.userA.read_resend_countdown(timeout=20)
        assert first is not None, "未读到重发倒计时(「重新发送(Ns)」OCR 未命中)"
        second = self.userA.read_resend_countdown(timeout=20)
        assert second is not None, "二次读取倒计时失败"
        assert second < first, f"倒计时未递减: {first} → {second}"
        # 步骤 3(S3):返回手机号步,同号再次提交 → 切回验证码步剩余时间延续
        self.userA.back_to_phone_step()
        self.userA.enter_sms_code_step(self.userA.phone)
        third = self.userA.read_resend_countdown(timeout=20)
        assert third is not None, "同号复用后未读到倒计时(未切回验证码步?)"
        assert third <= second, (
            f"冷却内同号复用倒计时被重置({second} → {third}):同号复用发码了, "
            "与「剩余时间延续/零新请求」契约相悖")
        # 步骤 4(S5):再返回手机号步,改号提交 → 倒计时重置 ~60
        self.userA.back_to_phone_step()
        self.userA.fill_phone_number("13900000003")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "改号 13900000003 提交后未进入验证码输入页(改号发码链路失效?)")
        fourth = self.userA.read_resend_countdown(timeout=20)
        assert fourth is not None, "改号提交后未读到倒计时"
        assert fourth > third and fourth >= 55, (
            f"改号后倒计时未重置(改号前 {third} → 改号后 {fourth}), "
            "与「改号清零重发 60s」契约相悖")
