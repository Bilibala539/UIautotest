# CASE-ID: music-NEG-006
"""Swan 回归·M07 平台授权:Qobuz 授权页外域跳转中断→授权可重入不锁死(music-NEG-006)。

步骤→AW 映射:
  1. 平台页 Qobuz 行点 [+] 发起授权(OAuth WebView,authUrl 服务端下发)
     → tap_platform_row_plus('qobuz')
  2. H5 授权页内点外域链接(如「忘记密码」;TBD·图像) → find_text_by_ocr
     探测命中才点击,未出现则按页面实际态继续(页面内容未标定)
  3. 外域页按系统返回 → press_back(),宿主不崩溃以 OCR 变体锚探活
  4. 退出 H5 回平台页重新发起 → 平台页未达时 press_back()(条件退避,根级
     禁返回键) → 再次 tap_platform_row_plus('qobuz') 重入成功

cleanup: dismiss_auth_popup + 条件 press_back 关闭 WebView/弹层回平台页;
框架每用例冷启动。
B 标定说明:Qobuz OAuth H5 页(mock 渲染)内容未截模板,「忘记密码」等
外域入口与登录页锚均为探测式;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg006QobuzAuthReentry(BaseTest):
    """Qobuz OAuth 外域跳转中断:授权链路可重入不锁死。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_h5_interrupt_reentry(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qobuz") != "unauthorized":
            pytest.skip("Qobuz 行非未授权态,授权无法从 [+] 发起(账号态自适配)")
        self.userA.tap_platform_row_plus("qobuz")
        if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
            self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
            "发起后未出现 Qobuz OAuth 外域登录页(WebView 未拉起或加载失败)")
        if self.userA.find_text_by_ocr("忘记密码", timeout=5) is not None:
            self.userA.click_text("忘记密码", timeout=3)
            self.userA.assert_any_text(["忘记密码", "找回", "重置", "登录"])
        self.userA.press_back()
        self.userA.assert_any_text(["登录", "忘记密码", "Qobuz", "QQ音乐"])
        if self.userA.find_text_by_ocr("QQ音乐", timeout=3) is None:
            self.userA.press_back()
        assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
            "退出 H5 后未回到平台页(WebView 未关闭)")
        self.userA.assert_no_auth_error()
        self.userA.tap_platform_row_plus("qobuz")
        if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
            self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
            "中断后重新发起未再次进入 OAuth 登录页(疑 auth_in_progress 误锁)")
        self.userA.dismiss_auth_popup()
        if self.userA.find_text_by_ocr("QQ音乐", timeout=2) is None:
            self.userA.press_back()
