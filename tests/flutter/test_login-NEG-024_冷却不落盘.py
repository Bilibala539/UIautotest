# CASE-ID: login-NEG-024
"""Swan 回归·会话与登录:发码倒计时客户端不落盘(login-NEG-024)。

步骤→AW 映射:
1. 验证码形态提交发码(真实 SMS #1)进入输码页(倒计时运行中);
2. 冷启动重启(relaunch_app) → 断言落回登录页验证码形态(assert_sms_form);
3. 同号再次提交发码 → 直接进入输码页(客户端倒计时丢失未拦截,真实 SMS #2)。
注:服务端频繁限制为观察面——若 15-20s 内二次发码被服务端拒绝,步骤 3 的
   enter_sms_code_step 到位断言失败即「服务端兜底触发」的观察结果,属本条
   已知风险面(report.notes 已说明)。
cleanup: 真实发码 ×2,网关旧码由后续取码取最新覆盖,无遗留态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestCountdownNotPersisted(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_countdown_not_persisted(self) -> None:
        # 步骤 1:首次发码进入输码页
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        # 步骤 2:冷启动重启 → 落回验证码形态
        self.userA.relaunch_app(self.userA.package)
        self.userA.assert_sms_form()
        # 步骤 3:同号二次发码直通(倒计时未落盘)
        self.userA.enter_sms_code_step(self.userA.phone)
