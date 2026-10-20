# CASE-ID: music-POS-042
"""Swan 回归·M07 平台授权:Qobuz授权至OAuth页(music-POS-042)。

步骤→AW 映射(7.7 授权族,专属型弹层,止于 OAuth WebView 打开):
  1. Qobuz 行 [+] 钮 → platform_row_state 闸门(非未授权即 skip=YAML
     授权态预置)+ tap_platform_row_plus → 授权确认底部弹层(专属型)
  2. 弹层确认 → confirm_auth_dialog → OAuth 2.0 WebView 打开外域登录页
     (变体词探测:Log/Email/登录等登录页专属词,避开平台行「Qobuz」
     文案防 WebView 未起时误匹配宿主行)
  3. 不输入任何凭据条件关闭 WebView → 授权以取消收尾

cleanup: 关闭 WebView 即取消,无状态残留,无服务端绑定写。
B 标定说明:Qobuz OAuth 外域登录页为第三方页面,锚词真机标定后收紧,
见 package_report.json template_needs。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos042QobuzAuthOauth(BaseTest):
    """Qobuz 授权弹层→OAuth WebView 打开→取消收束链路可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_auth_to_oauth(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:Qobuz 行须未授权(授权态预置)
        state = self.userA.platform_row_state("qobuz")
        if state != "unauthorized":
            pytest.skip(
                f"Qobuz 行授权态={state}(YAML 需未授权预置;禁止解绑还源)")
        # 步骤 1:[+] 钮 → 授权确认底部弹层(专属型)
        self.userA.tap_platform_row_plus("qobuz")
        self.userA.assert_any_text(["确认", "授权"])
        # 步骤 2:确认 → OAuth WebView 外域登录页(登录页专属词探测)
        oauth = None
        for word in ("Log", "Email", "登录", "Sign", "Password"):
            oauth = self.userA.find_text_by_ocr(word, timeout=3)
            if oauth is not None:
                break
        assert oauth is not None, (
            "Qobuz 确认后未捕获 OAuth WebView 登录页(变体词全未命中;"
            "外域登录页加载失败或锚待真机标定,见 template_needs)")
        # 步骤 3:不输入凭据条件关闭 WebView(登录页非平台根级,可返回)
        self.userA.press_back()
        if (self.userA.find_text_by_ocr("Log", timeout=2) is not None
                or self.userA.find_text_by_ocr("Email", timeout=1) is not None
                or self.userA.find_text_by_ocr("登录", timeout=1) is not None):
            self.userA.press_back()  # WebView 内层历史页兜底再退一次
        self.userA.dismiss_auth_popup()
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
