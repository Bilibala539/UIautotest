# CASE-ID: music-NEG-002
"""Swan 回归·M07 平台授权:QQ 授权挂起中重复发起:定向提示不重拉(music-NEG-002)。

步骤→AW 映射:
  1. 发起 QQ 授权进入挂起 → tap_platform_row_plus('qq') + confirm_auth_dialog(),
     进度弹层以「取消」钮 [OCR] 探活
  2. 进度弹层存活时再次点 QQ 行 [+] → 再次 tap_platform_row_plus('qq')
     (latest-wins 策略下预期互斥而非覆盖)
  3. 观察定向提示 → wait_toast('授权')(坑 7 auth_in_progress 定向提示类;
     具体映射文案未标定,以含「授权」的 toast 捕获为 B 口径)

cleanup: dismiss_auth_popup 取消挂起授权(cancelAuthorize),回平台页确认
无残留弹层;框架每用例冷启动。
B 标定说明:auth_in_progress 定向提示文案与进度弹层遮挡程度未真机标定,
文案标定后应收紧为精确匹配(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg002AuthInProgressHint(BaseTest):
    """QQ 挂起中重复发起:auth_in_progress 定向提示,不重复拉起。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_pending_retrigger_in_progress_hint(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "unauthorized":
            pytest.skip("QQ 行非未授权态,授权挂起链路无法从 [+] 发起(账号态自适配)")
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
            "确认后授权进度弹层未出现(第一次授权未进入挂起)")
        self.userA.tap_platform_row_plus("qq")
        assert self.userA.wait_toast("授权", timeout=5), (
            "挂起中重复发起未捕获授权类定向提示(auth_in_progress 映射文案待标定)")
        self.userA.dismiss_auth_popup()
        self.userA.assert_no_auth_error()
