"""YAML 用例通用驱动(① loader → 执行)。

不生成 py 脚本:YAML 用例(knowledge/swan/cases/driver/**/*.yaml)由本驱动
在 pytest 收集时参数化加载,执行时按步骤把 action 分派到 SwanBusiness /
基础 AW 方法。文字用例→YAML→执行的链路里,这一层是唯一的执行机器。

允许名单(两源合并,新增业务方法自动纳入):
  - 基础 AW 显式名单(BoolActions:返回值参与断言)
  - SwanBusiness 全部公开方法(内部 assert,失败即抛)

特殊插值变量:
  ${phone}  测试账号手机号(.env.local SWAN_PHONE)
  ${otp}    实时验证码(otp-gateway,取码耗时,只在需要时取)
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import pytest

from conftest import BaseTest
from utils.aw.business.swan import SwanBusiness
from utils.case_loader import CaseLoadError, discover_cases, interpolate, load_case

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

# 返回 bool 的基础 AW 动作:assert=false 时不校验,否则断言为真
_BOOL_ACTIONS = {
    "wait_accessibility", "accessibility_exists", "text_exists",
    "text_not_exists", "image_exists", "input_text", "clear_input",
    "tap", "swipe", "swipe_up", "swipe_down", "click_text",
}
# 显式放行的基础 AW 动作(返回 None 或对象,不做布尔断言)
_BASE_ACTIONS = set(_BOOL_ACTIONS) | {
    "take_screenshot", "relaunch_app", "press_back", "click_accessibility",
    "long_press", "go_home", "dump_semantics", "print_semantics",
}


def _business_actions() -> set[str]:
    return {
        name for name in dir(SwanBusiness)
        if not name.startswith("_") and callable(getattr(SwanBusiness, name, None))
    }


_ALLOWED_ACTIONS = _BASE_ACTIONS | _business_actions()
_CASE_DIR = Path(__file__).resolve().parents[2] / "knowledge" / "swan" / "cases" / "driver"
_CASE_FILES = discover_cases(_CASE_DIR)
_CASE_IDS = [p.stem for p in _CASE_FILES]


@pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="YAML 驱动用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)
class TestCaseDriver(BaseTest):
    """YAML 用例通用驱动:每个 YAML 文件参数化为一条 pytest 用例。"""

    def setup(self):
        self.userA = self.users("swanuserA")
        # 每条用例开始:确保 App 在前台 + 首启弹窗自动处置
        # (2026-09-22 用户拍板:打开 App 后框架级检测弹窗;新装包首启的
        # 隐私协议弹窗不点掉,登录页语义树虽在但不可交互)
        starter = getattr(self.userA.driver, "start_app", None)
        if starter is not None:
            starter(self.userA.package)
            self.userA.dismiss_app_popups()

    # ---------- 插值上下文 ----------

    def _context(self) -> dict:
        context = dict(os.environ)
        phone = self.userA.phone
        context["phone"] = phone

        class _OtpVar:
            """惰性取码:只有 ${otp} 真被插值到才请求网关(取码有耗时)。"""

            def __str__(self):
                from utils.otp_client import OtpClient
                record = OtpClient().get_code(phone)
                return str(record["code"])

        context["otp"] = _OtpVar()
        return context

    # ---------- 步骤分派 ----------

    def _resolve(self, action: str):
        if action not in _ALLOWED_ACTIONS:
            raise CaseLoadError(
                f"action '{action}' 不在允许名单内(基础 AW {len(_BASE_ACTIONS)} 个 + "
                f"SwanBusiness 公开方法 {len(_business_actions())} 个)"
            )
        return getattr(self.userA, action)

    def _run_step(self, index: int, step: dict, context: dict) -> None:
        action, args = step["action"], step["args"]
        desc = step.get("desc") or action
        resolved = interpolate(args, context)
        print(f"[step {index}] {desc} -> {action}({resolved})")
        fn = self._resolve(action)
        result = fn(**resolved)
        if step["assert"] and action in _BOOL_ACTIONS:
            assert result, f"step[{index}] {desc}: {action} 返回 {result!r},断言失败"

    # ---------- 用例执行 ----------

    def _wait_through_popups(self, key: str, timeout: float) -> bool:
        """等待语义节点出现,失败间隙周期性处置异步弹窗。

        首启弹窗(隐私/平台授权/系统权限)可能在 start_app 后数秒才异步弹出,
        一次性前置处置会错过;先短等待,失败则处置弹窗再等,直到超时。
        """
        deadline = time.monotonic() + timeout
        while True:
            if self.userA.wait_accessibility(key, timeout=4.0):
                return True
            if time.monotonic() >= deadline:
                return False
            self.userA.dismiss_app_popups()

    def _normalize_login_state(self, timeout: float = 15.0) -> None:
        """登录模块前置归一化(移植自登录试点 _ensure_fresh_sms_form)。

        已登录 → 登出;停在脏表单(密码形态/错误提示/验证码步残留) →
        重启重置(登录页无状态持久化)。结束态:全新验证码登录页。
        """
        K = SwanBusiness
        if self.userA.accessibility_exists(K.KEY_TAB_ME):
            self.userA.logout_if_needed()
        if (self.userA.accessibility_exists(K.KEY_PASSWORD_FIELD)
                or self.userA.accessibility_exists(K.KEY_ERROR_TEXT)
                or self.userA.accessibility_exists(K.KEY_CODE_FIELD)):
            self.userA.relaunch_app(self.userA.package)
            assert self._wait_through_popups(
                K.KEY_LOGIN_PAGE, timeout
            ), "重启 App 后未回到登录页"
        assert self._wait_through_popups(
            K.KEY_USE_PASSWORD_BUTTON, timeout
        ), "未停在验证码登录形态(login_use_password_button 未出现)"

    def _execute_case(self, case_path: Path) -> None:
        case = load_case(case_path)
        context = self._context()
        print(f"[case {case.case_id}] {case.title}(module={case.module}, priority={case.priority})")
        if case.source:
            print(f"[case {case.case_id}] 来源: {case.source}")
        if case.module == "login":
            print(f"[case {case.case_id}] 前置归一化: 登录态重置")
            self._normalize_login_state()
        for index, step in enumerate(case.steps, 1):
            self._run_step(index, step, context)
        if case.expected:
            print(f"[case {case.case_id}] 预期: {case.expected}")


def _parametrize(cls) -> None:
    """给 TestCaseDriver 注入执行方法:每个 YAML 文件一条 pytest 用例。

    setup 由 conftest 的 _auto_test_lifecycle autouse fixture 自动调用,
    生成方法只负责触发执行。
    """

    def make_test(case_file: Path):
        def run(self: TestCaseDriver):
            self._execute_case(case_file)
        run.__doc__ = f"YAML 驱动用例: {case_file.name}"
        return run

    for case_file, case_id in zip(_CASE_FILES, _CASE_IDS):
        setattr(cls, f"test_yaml_{case_id}", make_test(case_file))


_parametrize(TestCaseDriver)
