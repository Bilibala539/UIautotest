# CASE-ID: login-NEG-022
"""Swan 回归·会话与登录:错误码自动提交后清码与回填防重(login-NEG-022)。

步骤→AW 映射(ADD1 复审强化:补清码契约 OCR 断言):
1. 进入验证码输入页(真实发码) → 填错误码「9999」满 4 位自动提交 →
   断言未进首页(assert_not_on_home)且仍在输码页(输入框 [图] 命中);
   清码契约断言:text_not_exists("9999") —— 失败后验证码框自动清空
   (resetAfterFailure 契约;页面无其他「9999」文案源:发码提示/倒计时/
   手机号 13555555555 均不含该串,OCR 反断言干净);
2. 同码回填(fill_sms_code 追加语义,框已清空故恰好 4 位) → 自动提交
   被防重护栏吞:断言仍未进首页 + 「9999」OCR 仍在屏(框未被失败清码
   循环消费 = 同码未发起提交的黑盒证据;若防重失效则会提交失败→清码,
   「9999」消失即暴露);
3. 点框清空改输「9998」恢复提交路径 → 提交失败清码:仍未进首页 +
   text_not_exists("9998")(改码后防重不命中、提交发生、失败清码契约
   再次生效)。
注:「失败提示文案锚」为模板回填面(report.template_needs 已登记);
   本条对已发真码做错误校验,不触发额外发码。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestWrongCodeResubmitGuard(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_wrong_code_resubmit_guard(self) -> None:
        # 步骤 1:错误码自动提交 → 停留输码页未进首页 + 失败清码契约
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        self.userA.fill_sms_code("9999")
        self.userA.assert_not_on_home()
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "错误码提交后未停留在验证码输入页")
        assert self.userA.find_text_by_ocr("9999", timeout=8) is None, (
            "失败后验证码框未自动清空(「9999」OCR 仍在,清码契约相悖)")
        # 步骤 2:同码回填(防重面) → 仍未进首页且同码未被消费
        self.userA.fill_sms_code("9999")
        self.userA.assert_not_on_home()
        assert self.userA.find_text_by_ocr("9999", timeout=5) is not None, (
            "同码回填后「9999」不在屏(被提交-清码循环消费,防重护栏未生效)")
        # 步骤 3:清空改一位恢复提交 → 提交失败清码再次生效
        self.userA.click_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("9998")
        self.userA.assert_not_on_home()
        assert self.userA.find_text_by_ocr("9998", timeout=8) is None, (
            "改码 9998 提交后未清码(防重不命中应恢复自动提交并失败清码)")
