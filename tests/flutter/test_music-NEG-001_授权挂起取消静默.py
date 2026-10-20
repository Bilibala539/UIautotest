# CASE-ID: music-NEG-001
"""Swan 回归·M07 平台授权:QQ 授权挂起中弹层取消:静默收束不报错(music-NEG-001)。

步骤→AW 映射:
  1. 平台页 QQ 行点 [+] 发起授权 → tap_platform_row_plus('qq')(行带 [+] 定位链)
  2. 确认弹层点确认发起 → confirm_auth_dialog();进度弹层出现以「取消」钮
     [OCR] 探活(AIDL 挂起窗口,runWithPlatformAuthProgress 进度弹层)
  3. 挂起期间进度弹层点「取消」→ click_text('取消')(cancelAuthorize)
  4. 平台页无错误 toast → assert_no_auth_error()(user_cancel 静默类,坑 6;
     toast 存活 2-3s,断言为常驻错误文案尽力口径)
  5. QQ 授权态与发起前一致 → platform_row_state('qq') 仍为未授权

cleanup: 取消后进度弹层已关,dismiss_auth_popup 兜底清残留弹层;框架每用例
冷启动,平台页状态不跨用例残留。
B 标定说明:进度弹层标题/进度文案未截模板,以「取消」钮为弹层存活锚;QQ 行
[+] 模板真机补截后回填 template 实参(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg001AuthPendingCancelSilent(BaseTest):
    """QQ 授权挂起中取消:静默收束不报错,授权态不变。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_pending_cancel_silent(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "unauthorized":
            pytest.skip("QQ 行非未授权态,授权挂起链路无法从 [+] 发起(账号态自适配)")
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
            "确认后授权进度弹层未出现(「取消」钮未命中;疑 QQ 未装态走他路径,"
            "进度弹层文案待标定,见 package_report.json template_needs)")
        self.userA.click_text("取消", timeout=5)
        assert self.userA.find_text_by_ocr("取消", timeout=6) is None, (
            "点取消后进度弹层未关闭(「取消」钮仍存活)")
        self.userA.dismiss_auth_popup()
        self.userA.assert_no_auth_error()
        assert self.userA.platform_row_state("qq") == "unauthorized", (
            "取消后 QQ 授权态发生变化(应与发起前一致保持未授权)")
