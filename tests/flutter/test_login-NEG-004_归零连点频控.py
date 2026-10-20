# CASE-ID: login-NEG-004
"""Swan 回归·会话与登录:重发按钮归零后连点频控(login-NEG-004)。

步骤→AW 映射(ADD1 复审捞回):
1. 主号发码进入输码页(真实 SMS #1) → wait_resend_ready 轮询等冷却归零
   (「重新发送(N)」计数消失且可点态在屏);
2. 冷却归零后连续点「重新发送」×3(click_text 子串匹配:首点命中可点
   态;二、三点命中的是新冷却中的「重新发送(Ns)」禁用态,点击被客户端
   门控吞掉) → 首点放行触发重发(真实 SMS #2,倒计时重置 ~60),后续
   连点不二次发码;
3. 断言:仍在输码页(CODE_FIELD_BOX [图] 命中)且未进首页
   (assert_not_on_home) → read_resend_countdown 读 N ≥ 55(倒计时已被
   首点重置=放行证据;若门控失效连点多次发码,倒计时会被反复重置至
   置乱或页面异常);
注:S3「/captcha 请求计数=3」代理观察面为抓包注入面,UI 域以「连点后
   倒计时=首点重置值、页面态稳定」等价覆盖(report.notes 登记);风险
   口径同 NEG-024:服务端频繁限制失败时以页面停留观察为准。
cleanup: 真实发码 ×2(YAML 步骤必要范围:首条发码+归零重发)自然过期;
   未登录态保持,无遗留态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestResendSpamAfterCooldownZero(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_resend_spam_after_cooldown_zero(self) -> None:
        # 步骤 1:主号发码进入输码页,等冷却归零
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        self.userA.wait_resend_ready(timeout=90.0)
        # 步骤 2:归零后连点「重新发送」×3(首点放行重发,后续门控吞掉)
        for _ in range(3):
            self.userA.click_text("重新发送", timeout=5)
        # 步骤 3:仍在输码页未进首页,倒计时=首点重置值(≥55)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "连点重发后未停留在验证码输入页(页面态异常?)")
        self.userA.assert_not_on_home()
        reset = self.userA.read_resend_countdown(timeout=20)
        assert reset is not None, "连点后未读到重发倒计时(首点未放行重发?)"
        assert reset >= 55, (
            f"连点后倒计时 {reset}s 不足 55s:首点未重置冷却或门控失效多次发码, "
            "与「归零连点仅首点放行」契约相悖")
