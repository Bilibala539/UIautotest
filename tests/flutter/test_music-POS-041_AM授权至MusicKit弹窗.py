# CASE-ID: music-POS-041
"""Swan 回归·M07 平台授权:AM授权至MusicKit弹窗(music-POS-041)。

步骤→AW 映射(7.7 授权族,getToken→MusicKit 弹窗出现即止):
  1. Apple Music 行 [+] 钮 → platform_row_state 闸门(非未授权即 skip=
     YAML 授权态预置)+ tap_platform_row_plus → 授权确认弹框
  2. 弹框确认 → confirm_auth_dialog → 令牌获取后 MusicKit 授权弹窗
     (iOS 系统/MusicKit JS WebView 双通道;弹窗专属变体词探测,避开
     平台行「Apple Music」文案防误匹配宿主行)
  3. 弹窗取消(取消/Cancel,均无则弹窗顶栈返回等效关闭)→ 零副作用

cleanup: 系统弹窗取消即还原,无 musicUserToken 产生,无服务端绑定写。
B 标定说明:apple_auth_bg 弹层背景图与 MusicKit 弹窗锚待真机补截,
见 package_report.json template_needs;坑 4 developerToken 过期链不在
本例覆盖(测试机禁改设备时钟)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos041AmAuthMusickit(BaseTest):
    """AM 授权发起至 MusicKit 弹窗可达,取消零副作用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_am_auth_to_musickit(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:Apple Music 行须未授权(授权态预置)
        state = self.userA.platform_row_state("apple")
        if state != "unauthorized":
            pytest.skip(
                f"Apple Music 行授权态={state}(YAML 需未授权预置;"
                "禁止解绑还源)")
        # 步骤 1:[+] 钮 → 授权确认弹框
        self.userA.tap_platform_row_plus("apple")
        self.userA.assert_any_text(["确认", "授权"])
        # 步骤 2:确认 → MusicKit 授权弹窗(弹窗专属词,防平台行误匹配)
        anchor = None
        for word in ("MusicKit", "想要使用", "允许", "Authorize"):
            anchor = self.userA.find_text_by_ocr(word, timeout=4)
            if anchor is not None:
                break
        assert anchor is not None, (
            "AM 确认后未捕获 MusicKit 授权弹窗(变体词全未命中;"
            "developerToken 获取失败或弹窗锚待真机标定,见 template_needs)")
        # 步骤 3:系统弹窗取消,零副作用
        cancel = self.userA.find_text_by_ocr("取消", timeout=3)
        if cancel is None:
            cancel = self.userA.find_text_by_ocr("Cancel", timeout=2)
        if cancel is not None:
            self.userA.tap(cancel[0], cancel[1])
        else:
            self.userA.press_back()  # 弹窗顶栈返回等效关闭(非平台根级)
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
