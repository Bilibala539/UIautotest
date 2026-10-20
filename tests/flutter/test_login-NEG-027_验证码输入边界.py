# CASE-ID: login-NEG-027
"""Swan 回归·会话与登录:验证码输入位数/字符边界(login-NEG-027)。

步骤→AW 映射:
1. 进入验证码输入页(真实发码);
2. 填 3 位「123」→ 不自动提交:未进首页(assert_not_on_home)、仍在输码页
   (输入框 [图] 命中);
3. 点框续输字母「ab」→ 非数字被过滤:[OCR] 框内数字「123」保留(字母不回显);
4. 补第 4 位「4」→ 满位自动提交(错误码路径) → 仍未进首页。
注:5 位超长截断的框内观测与粘贴路径为回填面(4 格数字 OCR 区域未截),
   登记 report.template_needs;「123」整页 OCR 断言依赖页内无同串文本
   (发码文案/倒计时均不含)。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_LOGIN_CODE_FIELD_BOX
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestCodeFieldInputBounds(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_code_field_input_bounds(self) -> None:
        # 步骤 1:进入输码页
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        # 步骤 2:3 位不自动提交
        self.userA.fill_sms_code("123")
        self.userA.assert_not_on_home()
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=3) is not None, (
            "3 位即触发提交(应满 4 位才自动提交)")
        # 步骤 3:字母被过滤,数字保留
        self.userA.click_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=10)
        self.userA.input_text("ab")
        assert self.userA.find_text_by_ocr("123", timeout=5) is not None, (
            "字母未被过滤或已输数字丢失")
        # 步骤 4:补第 4 位自动提交(错误码路径) → 未进首页
        self.userA.fill_sms_code("4")
        self.userA.assert_not_on_home()
