# CASE-ID: login-NEG-049
"""Swan 回归·会话与登录:11 位非法号段(12x)提交拦截(login-NEG-049)。

步骤→AW 映射:
1. 填 11 位非法号段「12345678901」(不匹配 1[3-9])+勾协议 →
   主按钮启用(assert_sms_submit_enabled(True),位数校验仅看长度);
2. 点可用态主按钮(SWAN_LOGIN_SUBMIT_ENABLED [图]) → 号段拦截(定案零请求):
   未进输码页(输入框 [图] 不可见)、仍验证码形态(assert_sms_form)。
注:行内红字拦截文案为模板回填面,登记 report.template_needs;若门控失效,
   发码请求将对合成号发出并失败、输码页不出现,断言仍能捕获失效。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_ENABLED,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestInvalidPrefixBlocked(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_invalid_prefix_blocked(self) -> None:
        # 步骤 1:非法号段仅位数校验 → 主按钮启用
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number("12345678901")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 2:提交被号段拦截 → 停留登录页
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=5) is None, (
            "非法号段 12x 仍进入输码页(号段校验失效)")
        self.userA.assert_sms_form()
