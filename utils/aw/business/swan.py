"""Swan 项目业务方法（flutter 端）。

页面控件 key 约定（accessibility resource_id）与既有用例
``tests/flutter/test_swan_login_logout.py`` 保持一致。
"""
from __future__ import annotations

from utils.aw.base.flutter_base import FlutterBaseAW
from utils.aw.business.common import CommonBusinessMixin


class SwanBusiness(CommonBusinessMixin, FlutterBaseAW):
    """Swan 项目业务编排（flutter 端），Swan 专属业务方法放这里。"""

    # 登录页 accessibility key（✅ = 2026-09-08 真机 uiautomator dump 验证）
    KEY_LOGIN_PAGE = "login_page"                        # ✅
    KEY_PHONE_FIELD = "login_phone_field"                # ✅
    KEY_AGREEMENT = "login_agreement_checkbox"           # ✅
    KEY_SUBMIT = "login_submit_button"                   # ✅ 文案"下一步"
    KEY_USE_PASSWORD_BUTTON = "login_use_password_button"  # ✅ 右上角"密码登入"切换
    KEY_AREA_CODE_BUTTON = "login_area_code_button"      # ✅ 区号"+86"
    KEY_THIRD_WECHAT_BUTTON = "login_third_party_wechat_button"  # ✅
    KEY_THIRD_WEIBO_BUTTON = "login_third_party_weibo_button"    # ✅
    # ⚠️ 以下 key 尚未实机验证（需走到对应页面后按 dump 修正）
    KEY_PASSWORD_FIELD = "login_password_field"
    KEY_CODE_FIELD = "login_code_field"

    def login_with_password(self, phone: str, password: str) -> None:
        """密码登录，从任意初始状态开始，最终停在首页。"""
        if not self.accessibility_exists(self.KEY_PASSWORD_FIELD):
            self.click_accessibility(self.KEY_USE_PASSWORD_BUTTON)
        self.click_accessibility(self.KEY_PHONE_FIELD)
        self.input_text(phone)
        self.click_accessibility(self.KEY_PASSWORD_FIELD)
        self.input_text(password)
        self.press_back()
        self.click_accessibility(self.KEY_AGREEMENT)
        self.click_accessibility(self.KEY_SUBMIT)
        assert self.wait_text("推荐", "首页", timeout=20), "登录后未进入首页"

    def login_by_sms(self, phone: str, wait_code: float = 60.0) -> None:
        """验证码登录：切到验证码登录页 → 触发发送 → 平台取码 → 填码提交。"""
        if not self.accessibility_exists(self.KEY_CODE_FIELD):
            self.click_text("验证码登入", timeout=12)
        self.click_accessibility(self.KEY_PHONE_FIELD)
        self.input_text(phone)
        # 触发发送验证码；成功后网关才能从开发接口取到本次请求的验证码
        self.click_text("获取验证码", timeout=12)
        code = self._fetch_sms_code(phone, wait=wait_code)
        self.click_accessibility(self.KEY_CODE_FIELD)
        self.input_text(code)
        self.press_back()
        self.click_accessibility(self.KEY_AGREEMENT)
        self.click_accessibility(self.KEY_SUBMIT)
        assert self.wait_text("推荐", "首页", timeout=20), "登录后未进入首页"
