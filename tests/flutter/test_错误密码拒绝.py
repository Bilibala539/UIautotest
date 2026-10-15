# CASE-ID: aw-错误密码拒绝
# LINKED-CASE: login-NEG-008,login-NEG-029
"""Swan Flutter 错误密码被拒绝（原 test_swan_password_login.py，2026-10-12 拆分）。

业务方法复用 SwanBusiness，用例层只做编排与断言。

⚠️ 安全约束：连续 3 次密码错误可能锁号——本用例全程只试 1 次。
收尾约定：提交失败后的登录页表单会残留已填文本与协议勾选态，login_by_sms
盲点协议会反选导致「下一步」置灰、验证码发不出去（2026-09-08 实测踩坑），
故收尾重启 App 重置表单后再 login_by_sms 恢复登录态。
账号走环境变量 SWAN_PHONE / SWAN_PASSWORD（.env.local），用例中不硬编码。
断言辅助与表单归一化在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
结束状态：已登录停在首页（与设备初始状态一致）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_AGREEMENT_UNCHECKED,
    SWAN_LOGIN_PHONE_FIELD,
    SWAN_PASSWORD_FIELD,
)
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestWrongPasswordRejected(SwanLoginRegressionMixin, BaseTest):
    """错误密码被拒绝（只试 1 次，防锁号）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_wrong_password_rejected(self):
        """错误密码被拒绝（只试 1 次，防锁号）：断言未进首页且出现
        login_error_text 错误提示，收尾重启重置表单后 login_by_sms 恢复登录态。"""
        self.userA.ensure_fresh_sms_form()

        # 切到密码形态，输入正确手机号 + 错误密码（2026-10-13 key 迁移：全 [图]/[OCR]）
        self.userA.click_text("密码登入", timeout=10)
        self.userA.assert_password_form()
        self.userA.click_image(SWAN_LOGIN_PHONE_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text(self.userA.phone)
        self.userA.click_image(SWAN_PASSWORD_FIELD, timeout=10)
        self.userA.clear_input()
        self.userA.input_text("000000")
        self.userA.press_back()  # 收键盘（实测只收键盘不退出 App）
        self.userA.click_image(SWAN_LOGIN_AGREEMENT_UNCHECKED, timeout=5)
        self.userA.click_text("登录", timeout=5, region=self.userA._LOGIN_SUBMIT_REGION)

        # 断言未进首页：错误密码不应跳转首页（首页壳锚 [图] 反断言）
        assert not any(self.userA.probe_image(t, timeout=1) is not None
                       for t in self.userA._BOTTOM_NAV_TEMPLATES), (
            "错误密码竟进入了首页（底部导航 4 图出现），登录校验失效！")

        # 断言出现错误提示（实测：错误文案非 toast，是常驻节点
        # login_error_text，content-desc"密码错误，请重新输入！"；
        # key 迁移后用 [OCR] 定位错误文案）
        assert self.userA.find_text_by_ocr("密码错误", timeout=10) is not None, (
            "错误密码后未出现「密码错误」错误提示 [OCR]")

        # 收尾：提交失败后的登录页表单有残留（已填文本 + 协议已勾选，
        # login_by_sms 再点协议会反选导致"下一步"置灰），重启 App 重置表单
        # （登录页无状态持久化，重启回到全新验证码登录形态）
        self.userA.driver.stop_app(self.userA.package)
        self.userA.driver.start_app(self.userA.package)
        self.userA.assert_sms_form(timeout=30)
        self.userA.login_by_sms(self.userA.phone)
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
