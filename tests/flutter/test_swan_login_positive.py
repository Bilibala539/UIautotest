"""Swan 登录正向用例集(知识库 cases/login YAML → pytest 翻译试点)。

翻译来源:knowledge/swan/cases/login/SWAN-20260907-002-login-positive-cases.yaml
逐条可执行度评级与跳过原因见同目录 TRANSLATION-NOTES.md。本文件覆盖黑盒 UI
可自动化的 5 条:POS-002 / POS-005 / POS-007 / POS-010 / POS-011。
已在 test_swan_password_login.py 覆盖的 POS-003(密码登录)/POS-004(模式互切)
不重复实现;不可自动化的条目(隐私首启/第三方/注销/会话失效/切服)见 NOTES。

数据映射:YAML test_data_pool 为 TEST-SYNTHETIC 池(13800000002 等,测试环境
未必预置);本机真实账号走 .env.local(SWAN_PHONE),由 users("swan") 注入。
YAML 中的抓包级断言(请求体冗余字段/请求次数/SharedPreferences 三处同步)
超出黑盒 UI 能力,降级为 UI 态断言,详见 NOTES。

⚠️ 状态机约定(与 test_swan_password_login.py 一致):
- 每条用例开工前归一化到「全新验证码登录形态」(登出或重启重置)
- 模块结束状态:已登录停在首页
- 连续验证码/密码失败可能触发频控,每条用例最多发 1 次码、试 1 次错密码
"""
from __future__ import annotations

import os
import time

import pytest

from conftest import BaseTest
from utils.aw.business.swan import SwanBusiness

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 登录用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)


class TestSwanLoginPositive(BaseTest):
    """登录正向通道(知识库 YAML 翻译):主路径 / 协议联动 / 自动提交 / 冷启恢复 / 登出。"""

    def setup(self):
        self.user = self.users("swan")
        self.aw = self.user.aw
        self.phone = self.user.phone
        self.package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()

    # ---------- 前置归一化 ----------

    def _ensure_fresh_sms_form(self, timeout: float = 15.0):
        """归一化到全新验证码登录形态(空表单、协议未勾选)。

        已登录 → 登出;停在脏表单(密码形态/错误提示残留/验证码步) → 重启重置
        (登录页无状态持久化,重启回到全新验证码形态)。
        """
        if self.aw.accessibility_exists(SwanBusiness.KEY_TAB_ME):
            self.user.logout_if_needed()
        if (self.aw.accessibility_exists(SwanBusiness.KEY_PASSWORD_FIELD)
                or self.aw.accessibility_exists(SwanBusiness.KEY_ERROR_TEXT)
                or self.aw.accessibility_exists(SwanBusiness.KEY_CODE_FIELD)):
            self.aw.relaunch_app(self.package)
            assert self.aw.wait_accessibility(
                SwanBusiness.KEY_LOGIN_PAGE, timeout=timeout
            ), "重启 App 后未回到登录页"
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_USE_PASSWORD_BUTTON, timeout=timeout
        ), "未停在验证码登录形态(login_use_password_button 未出现)"

    def _ensure_logged_in(self):
        """确保已登录停在首页(前序用例被跳过时的防御)。"""
        if not self.aw.accessibility_exists(SwanBusiness.KEY_TAB_ME):
            self._ensure_fresh_sms_form()
            self.user.login_by_sms(self.phone)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_TAB_ME, timeout=20), "未进入首页"

    # ---------- 用例 ----------

    def test_pos002_sms_login_main_path(self):
        """POS-002 短信两步登录主路径:手机号+协议→发码→取码填入→自动提交进首页。

        对应 YAML 步骤1-4 的黑盒可断言子集:中间态(验证码输入页出现)与
        收口态(进首页)。请求体冗余字段/三处 token 同步为抓包级断言,不覆盖。
        """
        self._ensure_fresh_sms_form()

        # 步骤1-2:输入手机号,勾协议,点"下一步" → 切验证码步
        self.aw.enter_sms_code_step(self.phone)  # 内含 login_code_field 出现断言
        assert not self.aw.accessibility_exists(
            SwanBusiness.KEY_PASSWORD_FIELD
        ), "验证码步出现密码输入框,形态互斥被破坏"

        # 步骤3-4:取真实下发的码填入,满 4 位自动提交 → authenticated
        code = self.aw._fetch_sms_code(self.phone, wait=60.0)
        self.aw.fill_sms_code(code)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_TAB_ME, timeout=20), \
            "验证码填满后未自动提交进首页"
        # 结束状态:已登录停在首页

    def test_pos005_agreement_gating(self):
        """POS-005 协议勾选联动:未勾协议点主按钮不发码不切页,勾选后可提交。

        黑盒近似:未勾协议时点"下一步"应无响应(不出现验证码输入页);
        勾选后同操作应切到验证码步。第三方图标可点性不覆盖(不发起真实授权)。
        """
        self._ensure_fresh_sms_form()

        # 未勾协议:填手机号 → 点主按钮 → 不应进入验证码步
        self.aw.click_accessibility(SwanBusiness.KEY_PHONE_FIELD)
        self.aw.clear_input()
        self.aw.input_text(self.phone)
        self.aw.click_accessibility(SwanBusiness.KEY_SUBMIT)
        time.sleep(2)  # 给误放行的请求留出跳转窗口
        assert not self.aw.accessibility_exists(SwanBusiness.KEY_CODE_FIELD), \
            "未勾选协议时点击主按钮竟进入验证码步,协议联动失效!"
        assert self.aw.accessibility_exists(SwanBusiness.KEY_LOGIN_PAGE), \
            "未勾协议点主按钮后离开了登录页"

        # 勾选协议:同操作应切到验证码步(自动发码)
        self.aw.click_accessibility(SwanBusiness.KEY_AGREEMENT)
        self.aw.click_accessibility(SwanBusiness.KEY_SUBMIT)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_CODE_FIELD, timeout=15), \
            "勾选协议后点击主按钮未进入验证码步"
        # 结束状态:停在验证码步(倒计时冷却中,下条用例开工时重启重置)

    def test_pos007_auto_submit_boundary(self):
        """POS-007 验证码满 4 位自动提交:3 位不提交,第 4 位立即自动提交。

        黑盒近似:3 位时断言未进首页(无登录跳转);补第 4 位断言进首页。
        请求次数断言(3 位时 /user/login 请求数=0)为抓包级,不覆盖。
        """
        self._ensure_fresh_sms_form()
        self.aw.enter_sms_code_step(self.phone)
        code = self.aw._fetch_sms_code(self.phone, wait=60.0)
        assert len(code) == 4, f"验证码应为 4 位,实际 {len(code)} 位"

        # 前 3 位:不触发自动提交
        self.aw.fill_sms_code(code[:3])
        time.sleep(3)
        assert not self.aw.accessibility_exists(SwanBusiness.KEY_TAB_ME), \
            "仅输入 3 位验证码就进入了首页,满 4 位自动提交边界失效!"

        # 第 4 位:立即自动提交
        self.aw.fill_sms_code(code[3])
        assert self.aw.wait_accessibility(SwanBusiness.KEY_TAB_ME, timeout=20), \
            "输入第 4 位后未自动提交进首页"

    def test_pos010_cold_start_token_restore(self):
        """POS-010 登录成功后冷启动免登:杀进程重启直接进首页,不弹登录/隐私。

        黑盒断言:冷启动落地首页(tab_me),且无隐私弹窗/登录页残留。
        Authorization header 注入与日活节流为抓包级断言,不覆盖。
        """
        self._ensure_logged_in()

        self.aw.relaunch_app(self.package)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_TAB_ME, timeout=30), \
            "冷启动后未恢复登录态直达首页"
        assert not self.aw.accessibility_exists(SwanBusiness.KEY_LOGIN_PAGE), \
            "已持 token 冷启动竟出现登录页"
        # 结束状态:已登录停在首页

    def test_pos011_logout_point1_person_info(self):
        """POS-011 登出触发点1:个人信息页「退出登入」无二次确认直接登出回登录页。

        黑盒子集:四步路径断言 + 登出落地登录页。SharedPreferences/缓存清理
        为进程内断言,黑盒不覆盖。收尾 login_by_sms 恢复登录态(模块结束约定)。
        """
        self._ensure_logged_in()

        # me_page → me_user_profile_entry → person_info_page → logout
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_ME)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_ME_PROFILE_ENTRY, timeout=10), \
            "未进入我的页"
        self.aw.click_accessibility(SwanBusiness.KEY_ME_PROFILE_ENTRY)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_PERSON_INFO_PAGE, timeout=10), \
            "未进入个人信息页"
        # ⚠️ 同页存在 person_info_cancel_account_button(注销,不可逆),禁止触碰
        self.aw.click_accessibility(SwanBusiness.KEY_LOGOUT_BUTTON)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_LOGIN_PAGE, timeout=20), \
            "登出后未回到登录页"

        # 收尾:恢复登录态(模块结束状态约定:已登录停在首页)
        self.user.login_by_sms(self.phone)
        assert self.aw.wait_accessibility(SwanBusiness.KEY_TAB_ME, timeout=20), \
            "收尾恢复登录失败"
