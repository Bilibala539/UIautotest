# CASE-ID: login-NEG-026
"""Swan 回归·会话与登录:冷却中同号再提交直接切验证码步不重发(login-NEG-026)。

步骤→AW 映射(ADD1 复审捞回;数据口径:A 号以 userA.phone 替代 YAML
合成号——语义等价先例同 NEG-023,主号发码链路可达):
1. 主号发码进入输码页(真实 SMS) → read_resend_countdown 读 N1(冷却 ~60s
   运行中);
2. 页内返回箭头回手机号步(back_to_phone_step,NEG-005 定案通道) →
   同号再次提交(enter_sms_code_step) → 客户端冷却门控拦截:直接切回
   验证码步(不重发、无需重新输码) → 读 N2 ≤ N1:剩余时间延续——
   「零新请求/复用剩余冷却」的黑盒等价证据(若门控放行重发则倒计时
   重置 ~60 > N1 即暴露);
3. S3/S4(YAML 自标:清应用数据绕 UI 复验/抓包复核 /captcha 调用)为
   环境注入代理面,不在 UI 自动化能力域(report.notes 登记,OTHER 缺口
   仅此一面)。
注:发码 ×1(主号,本条流程必要最小量);S3/S4 代理计数面由 S2 倒计时
   延续观测等价覆盖。
cleanup: 真实发码 ×1 自然过期;未登录态保持,无遗留态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestCooldownResubmitDirectSwitch(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_resubmit_in_cooldown_switches_directly(self) -> None:
        # 步骤 1:主号发码进入输码页,读冷却 N1
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        first = self.userA.read_resend_countdown(timeout=20)
        assert first is not None, "发码后未读到重发倒计时(冷却未启动?)"
        # 步骤 2:返回手机号步 → 冷却中同号再提交 → 直切验证码步剩余时间延续
        self.userA.back_to_phone_step()
        self.userA.enter_sms_code_step(self.userA.phone)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "冷却中同号再提交未直接切回验证码步(客户端冷却门控失效?)")
        second = self.userA.read_resend_countdown(timeout=20)
        assert second is not None, "直切回验证码步后未读到倒计时"
        assert second <= first, (
            f"冷却中同号再提交触发重发(倒计时 {first} → {second}):门控未拦截, "
            "与「直接切验证码步不重发/零新请求」契约相悖")
