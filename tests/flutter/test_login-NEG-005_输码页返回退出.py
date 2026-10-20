# CASE-ID: login-NEG-005
"""Swan 回归·会话与登录:验证码输入页返回键退出应用(login-NEG-005 定案)。

步骤→AW 映射:
1. 进入验证码输入页(真实发码,enter_sms_code_step);
2. 填 1 位停手(fill_sms_code 追加语义,不足 4 位不自动提交);
3. press_back → 首次收软键盘、再次退出 App(定案):断言输码页锚(输入框 [图])、
   登录页锚(置灰「下一步」[图])、已登录首页锚(SWAN_TAB_HOME [图])全部不可见;
4. 冷启动重启 → relaunch_app,断言落回登录页验证码形态(assert_sms_form)。
注:步骤 5「重启后旧码探针」为回填面(旧码时效需网关配合),不落本脚本。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_BTN,
    SWAN_TAB_HOME,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestCodePageBackExitsApp(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_code_page_back_exits_app(self) -> None:
        # 步骤 1-2:进入输码页,填 1 位停手
        self.userA.ensure_fresh_sms_form()
        self.userA.enter_sms_code_step(self.userA.phone)
        self.userA.fill_sms_code("1")
        # 步骤 3:返回键(先收软键盘,再退出 App,与定案一致)
        self.userA.press_back()
        self.userA.press_back()
        assert self.userA.probe_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=3) is None, (
            "返回后输码页锚仍可见(未退出应用)")
        assert self.userA.probe_image(SWAN_LOGIN_SUBMIT_BTN, timeout=3) is None, (
            "返回后登录页锚仍可见(返回键行为为回登录页而非退出 App,与定案相悖)")
        assert self.userA.probe_image(SWAN_TAB_HOME, timeout=3) is None, (
            "返回后出现已登录首页锚(不应处于登录态)")
        # 步骤 4:冷启动重启 → 落回登录页验证码形态
        self.userA.relaunch_app(self.userA.package)
        self.userA.assert_sms_form()
