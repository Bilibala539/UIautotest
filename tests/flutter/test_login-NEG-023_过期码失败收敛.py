# CASE-ID: login-NEG-023
"""Swan 回归·会话与登录:过期验证码失败收敛与输入态不受扰(login-NEG-023)。

步骤→AW 映射(数据口径注记:过期码需真实可达码,网关白名单仅主号 135,故以
userA.phone 替代 YAML 合成号 13800000001,语义等价;过期=发码后真实等待 >5min):
1. 进输码页(真实发码)取码 → 探针式轮询等待过期(每 10s 探针输码页在屏,
   防中途离页);
2. 填过期码自动提交 → 登录失败:未进首页(assert_not_on_home)、停留输码页
   (输入框 [图] 在);错误文案本地化锚未截,登记 report.template_needs;
3. 修改输入(点框续输一位,S2 动作)后页面态不受扰:重发按钮可点态
   「重新发送」[OCR] 在(注:5min 等待下原倒计时已自然归零,S3「倒计时不受
   影响」以归零后可点态为观测面);
4. 对照:清空输入未请求过的随机码「1234」 → 同失败路径(停留、未进首页)。
注:S2「输入变化即清错」断言依赖错误文案锚(未截),动作已落、断言面登记
   template_needs;文案 locale 纪律(禁硬编码中文)待文案核准后补断言。
cleanup: 真实短信 ×1,码自然过期,无遗留态。
"""
from __future__ import annotations

import time

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestExpiredCodeRejected(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_expired_code_rejected(self) -> None:
        # 前置:进输码页取真实码
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        record = self.userA.otp.get_code(self.userA.phone, wait=60)
        code = str(record.get("code", ""))
        assert len(code) == 4, f"网关验证码异常: {code!r}"
        # 真实等待 >5min 过期(探针式轮询,防中途离页)
        deadline = time.monotonic() + 340
        while time.monotonic() < deadline:
            assert self.userA.probe_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=1) is not None, (
                "等待过期期间离开验证码输入页")
            self.userA.sleep(10)
        # 步骤 1:过期码自动提交 → 登录失败停留
        self.userA.fill_sms_code(code)
        self.userA.assert_not_on_home()
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "过期码提交后未停留在验证码输入页")
        # 步骤 2 动作 + 步骤 3:修改输入后页面态不受扰(重发可点态在)
        self.userA.click_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=10)
        self.userA.input_text("1")
        assert self.userA.find_text_by_ocr("重新发送", timeout=10) is not None, (
            "错误/改输后重发可点态不可见(页面态受扰)")
        # 步骤 4:对照——随机未请求码同失败路径
        self.userA.click_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("1234")
        self.userA.assert_not_on_home()
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "随机码提交后未停留验证码输入页(与过期码未走同收敛路径)")
