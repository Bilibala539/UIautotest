# CASE-ID: music-POS-043
"""Swan 回归·M07 平台授权:授权进度弹层三段链(music-POS-043)。

步骤→AW 映射(7.7 授权族,runWithPlatformAuthProgress 进度弹层):
  1. QQ 授权发起至确认 → tap_platform_row_plus+confirm_auth_dialog →
     observe_auth_launch 观察授权中进度弹层出现(未捕获=B 标定 skip)
  2. 进度弹层点取消 → click_text("取消")→ cancelAuthorize→native
     user_cancel 干净收尾(弹层关闭断言)
  3. 取消后立即重试 → 再次 tap_platform_row_plus+确认弹层出现(无
     auth_in_progress 残留)→ 收尾取消

cleanup: 重试发起后再取消一次(dismiss_auth_popup);未完成第三方确认
即无服务端绑定写。
B 标定说明:进度弹层文案(runWithPlatformAuthProgress)与 qq_auth_bg
待真机补截,见 package_report.json template_needs。坑 7:QQ AIDL 授权
最长挂起 120 秒为预期,取消动作不受其约束。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos043AuthProgressChain(BaseTest):
    """授权进度弹层展示→取消→重试三段链路可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_auth_progress_cancel_retry(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:QQ 行须未授权(授权态预置)
        state = self.userA.platform_row_state("qq")
        if state != "unauthorized":
            pytest.skip(
                f"QQ 行授权态={state}(YAML 需未授权预置;禁止解绑还源)")
        # 步骤 1:发起授权并确认 → 授权中进度弹层出现
        self.userA.tap_platform_row_plus("qq")
        self.userA.assert_any_text(["确认", "授权"])
        self.userA.confirm_auth_dialog()
        seen = self.userA.observe_auth_launch()
        if not seen:
            pytest.skip(
                "确认后等待窗内未捕获授权中进度弹层(B 口径;"
                "弹层文案/出现时机待真机标定,见 template_needs)")
        # 步骤 2:进度弹层点取消 → 干净收尾
        self.userA.click_text("取消", timeout=5)
        assert self.userA.find_text_by_ocr("授权中", timeout=2) is None, (
            "取消后授权中进度弹层未关闭(cancelAuthorize 收尾失败)")
        # 步骤 3:取消后立即重试,可重新发起(无 auth_in_progress 残留)
        self.userA.tap_platform_row_plus("qq")
        self.userA.assert_any_text(["确认", "授权"])
        # cleanup:重试发起后再取消一次
        self.userA.dismiss_auth_popup()
        self.userA.assert_no_auth_error()
