# CASE-ID: login-NEG-025
"""Swan 回归·会话与登录:同号返回复用剩余冷却 vs 改号清零(login-NEG-025)。

步骤→AW 映射(ADD1 复审捞回,数据口径注记:A 号以 userA.phone 替代 YAML
合成号 13800000001——语义等价先例同 NEG-023,主号发码链路可达;B 号保持
YAML 合成号 13800000002,POS-020 先例:合成号发码链路 success 可走不取码):
1. 主号发码进入输码页(真实 SMS #1) → read_resend_countdown 读 N1
   (冷却 ~60s 运行中);
2. S1:页内返回箭头回手机号步(back_to_phone_step,NEG-005 定案通道) →
   同号再次提交(enter_sms_code_step) → 直接切验证码步 → 读 N2 ≤ N1:
   剩余时间延续(冷却按号延续;若重发则重置 ~60 > N1 即暴露——「零新
   请求」代理面的黑盒等价证据);
3. S2:再返回手机号步 → 改号 13800000002 提交(真实/合成发码 #2) →
   进验证码步 → 读 N3 ≥ 55 且 N3 > N2:改号清零重发,倒计时重置 ~60。
注:S3「改号绕过风险面记录」为 YAML 自标记录注记步,不落断言;S1/S2 的
   代理计数面由倒计时延续/重置观测等价覆盖(report.notes 登记)。
cleanup: 真实发码 ×2 自然过期;未登录态保持,无遗留态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_ENABLED,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestCooldownReuseVsReset(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_same_phone_cooldown_kept_new_phone_reset(self) -> None:
        # 前置:主号发码进入输码页
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        first = self.userA.read_resend_countdown(timeout=20)
        assert first is not None, "发码后未读到重发倒计时(冷却未启动?)"
        # 步骤 1(S1):冷却中返回手机号步,同号再次提交 → 剩余时间延续
        self.userA.back_to_phone_step()
        self.userA.enter_sms_code_step(self.userA.phone)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "冷却中同号再提交未直接切回验证码步(门控拦截失效?)")
        second = self.userA.read_resend_countdown(timeout=20)
        assert second is not None, "同号复用后未读到倒计时"
        assert second <= first, (
            f"同号复用倒计时被重置({first} → {second}):冷却未按号延续, "
            "与「同号复用剩余冷却/零新请求」契约相悖")
        # 步骤 2(S2):返回后改号 B 提交 → 倒计时清零重发
        self.userA.back_to_phone_step()
        self.userA.fill_phone_number("13800000002")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "改号 13800000002 提交后未进入验证码输入页(改号发码链路失效?)")
        third = self.userA.read_resend_countdown(timeout=20)
        assert third is not None, "改号提交后未读到倒计时"
        assert third > second and third >= 55, (
            f"改号后倒计时未清零重置(改号前 {second} → 改号后 {third}), "
            "与「改号立即清零正常发码」契约相悖")
