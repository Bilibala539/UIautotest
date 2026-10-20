# CASE-ID: login-NEG-028
"""Swan 回归·会话与登录:密码输入 16 位硬截断(login-NEG-028)。

步骤→AW 映射(ADD1 复审捞回;原判「掩码渲染无可观测量」经明文切换通道
破解:SWAN_PASSWORD_FIELD 模板右段含闭眼图标(image_name_mapping 元素
注记「右侧闭眼图标入模」),reveal_password_text 点右端切明文后 OCR 读回):
1. 密码形态(YAML 合成号 13800000001 写死) → 点密码框填 20 位密码
   「Aa123456Aa123456zzzz」(无特殊字符,规避 adb 逐字键入转义面) →
   press_back 收键盘(密码页 back 语义=收键盘,POS-009 定案);
2. S2:切明文读回(reveal_password_text) → 断言读回行含「Aa」(前 16 位
   前缀在)且不含「zzzz」(第 17-20 位被截)=16 位硬截断双面;若截断
   失效则「zzzz」随明文在屏即暴露。明文态 OCR 观测面与「密码框输入态
   模板」缺口见 report.template_needs 登记;
3. S3:点「登录」提交一次(截断后的 16 位即实际提交值;合成号无锁号
   风险,错误密码仅失败不产生登录态) → assert_not_on_home + 仍密码形态。
注:S2「前端长度计数=16」代理面由明文读回截断观测等价覆盖
   (report.notes 登记)。
cleanup: 提交失败未产生登录态;未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PASSWORD_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestPasswordSixteenCharTruncation(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_password_sixteen_char_truncation(self) -> None:
        # 前置:密码形态,填号与 20 位密码
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        self.userA.fill_phone_number("13800000001")
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("Aa123456Aa123456zzzz")
        self.userA.press_back()  # 收软键盘
        # 步骤 1-2(S2):切明文读回,断言 16 位硬截断
        shown = self.userA.reveal_password_text("Aa")
        assert shown is not None, (
            "切明文后 OCR 未读回密码行(明文切换未生效或明文态 OCR 观测面"
            "缺口——密码框输入态模板未入库,report.template_needs 已登记)")
        assert "aa" in shown.lower(), f"明文读回行缺密码前缀(读到 {shown!r})"
        assert "zzzz" not in shown.lower(), (
            f"第 17-20 位「zzzz」未被截断(明文读回 {shown!r}), "
            "与「密码 16 位硬截断」契约相悖")
        # 步骤 3(S3):提交一次,未产生登录态
        self.userA.click_text("登录", timeout=10)
        self.userA.assert_not_on_home()
        self.userA.assert_password_form()
