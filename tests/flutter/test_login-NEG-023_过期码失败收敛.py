# CASE-ID: login-NEG-023
"""Swan 回归·会话与登录:过期验证码失败收敛与输入态不受扰(login-NEG-023)。

步骤→AW 映射(数据口径注记:过期码需真实可达码,网关白名单仅主号 135,故以
userA.phone 替代 YAML 合成号 13800000001,语义等价;过期=发码后真实等待 >5min):
1. 进输码页(真实发码)取码 → 探针式轮询等待过期(每 10s 探针输码页在屏,
   防中途离页);
2. 填过期码自动提交 → 登录失败:未进首页(assert_not_on_home)、停留输码页
   (输入框 [图] 在);错误文案本地化锚未截,登记 report.template_needs;
3.【YAML locator 与实机不符,偏差如实声明】YAML 步骤 2 locator=
   login_phone_field(点击手机号输入框、改一位号码字符);实机输码页无手机号
   输入框——knowledge/swan/pages/swan_验证码输入页.md(2026-09-08 真机
   uiautomator dump 转正)关键元素仅 login_page/login_code_field/重发倒计时,
   手机号仅以顶部静态提示「验证码已经发送至 +86…」呈现,不可编辑。采用的
   替代动作及理由:点击验证码框(该页唯一可编辑输入)→清空已满 4 位码→重输
   3 位「123」(不满 4 位不触发自动提交)。YAML 步骤 2 expect「输入变化即清
   错」的机制前提是输入内容真实变化(onChanged→clearLoginError/
   _clearInlineError),清空构成真实变化;不采用「续输第 5 位」——满 4 位自动
   提交语义下第 5 位输入可能被输入上限丢弃、内容不变,onChanged 不触发,
   动作可能空转(原实现缺陷,本轮修正)。「输入变化即清错」断言口径:错误
   文案锚未截、文案未核准(report.template_needs 已登记),不伪造文案断言;
   OCR 可断等价面=输入变化后页面态不受扰(停留输码页+验证码框 [图] 在+
   「重新发送」可点态在),清错直证(错误条消失)待文案核准后补断言;
4. 对照:清空输入未请求过的随机码「1234」 → 同失败路径(停留、未进首页)。
cleanup(YAML recovery「重新发码」落实):步骤 4 失败停留态下点「重新发送」
   对既有号码 userA.phone 真实发码 ×1,不读码(不调 otp.get_code),倒计时
   重启(read_resend_countdown 非 None)即发码生效断言;新码自然过期,冷启动
   模型清场,无遗留态。
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
        # 步骤 2(替代动作,偏差声明见 docstring 第 3 条):点击验证码框→清空
        # 已满 4 位码→重输 3 位(不满 4 不触发自动提交)——保证输入内容真实
        # 变化,对齐 YAML「输入变化即清错」的触发前提;输码页无手机号框可点
        # (YAML locator=login_phone_field 与实机不符,已如实声明)
        self.userA.click_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("123")
        # 步骤 3:输入变化后页面态不受扰(OCR 可断等价面,清错直证待文案核准)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "输入变化后验证码输入框不可见(输码页页面态受扰)")
        self.userA.assert_not_on_home()
        assert self.userA.find_text_by_ocr("重新发送", timeout=10) is not None, (
            "错误/改输后重发可点态不可见(页面态受扰)")
        # 步骤 4:对照——随机未请求码同失败路径
        self.userA.click_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("1234")
        self.userA.assert_not_on_home()
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is not None, (
            "随机码提交后未停留验证码输入页(与过期码未走同收敛路径)")
        # cleanup(YAML recovery「重新发码」落实):失败停留态下点「重新发送」
        # 对既有号码真实发码,不读码;倒计时重启即发码生效断言
        self.userA.click_text("重新发送", timeout=10)
        assert self.userA.read_resend_countdown(timeout=30) is not None, (
            "cleanup 重新发码后倒计时未重启(发码未生效)")
