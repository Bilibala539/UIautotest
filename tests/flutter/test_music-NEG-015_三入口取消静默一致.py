# CASE-ID: music-NEG-015
"""Swan 回归·M07 平台授权:授权取消跨入口静默一致性·三入口(music-NEG-015)。

步骤→AW 映射(三入口各自复用同族单例口径,坑 6 user_cancel 静默类):
  1. QQ 授权挂起后取消 → tap_platform_row_plus('qq') + confirm_auth_dialog()
     + click_text('取消'),断言进度弹层关闭 → assert_no_auth_error()
  2. 网易云 H5 授权页中途返回 → tap_platform_row_plus('netease',
     template=SWAN_NETEASE_PLUS_BTN) + confirm 探测 → 登录页锚 → press_back()
     → assert_no_auth_error()
  3. Qobuz OAuth 打开后立即退出 → tap_platform_row_plus('qobuz') + confirm
     探测 → 登录页锚 → press_back() → assert_no_auth_error()
  4. 一致性 = 三入口同一静默断言口径(常驻错误文案零出现)

cleanup: 各入口退出后已回平台页;框架每用例冷启动。
B 标定说明:入口按平台行授权态自适配——某行已授权则该入口无法从 [+] 发起
(不做取消授权破坏性操作),全部入口不可用时整例跳过;网易云/Qobuz H5 页锚
与 QQ [+] 模板待真机补截(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_NETEASE_PLUS_BTN


class TestMusicNeg015CancelSilentConsistency(BaseTest):
    """三发起入口取消均静默(user_cancel),跨入口提示行为一致。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_three_entry_cancel_silent(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        ran = False
        if self.userA.platform_row_state("qq") == "unauthorized":
            # 入口 1:QQ 挂起中取消(NEG-001 口径)
            self.userA.tap_platform_row_plus("qq")
            self.userA.confirm_auth_dialog()
            assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
                "入口 1:确认后授权进度弹层未出现")
            self.userA.click_text("取消", timeout=5)
            assert self.userA.find_text_by_ocr("取消", timeout=6) is None, (
                "入口 1:点取消后进度弹层未关闭")
            self.userA.assert_no_auth_error()
            ran = True
        if self.userA.platform_row_state("netease") == "unauthorized":
            # 入口 2:网易云 H5 中途返回(NEG-004 口径,禁区 1 不输入凭据)
            self.userA.tap_platform_row_plus(
                "netease", template=SWAN_NETEASE_PLUS_BTN)
            if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
                self.userA.confirm_auth_dialog()
            assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
                "入口 2:H5 外域登录页未出现")
            self.userA.press_back()
            assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
                "入口 2:中途返回后未回到平台页")
            self.userA.assert_no_auth_error()
            ran = True
        if self.userA.platform_row_state("qobuz") == "unauthorized":
            # 入口 3:Qobuz OAuth 打开后立即退出
            self.userA.tap_platform_row_plus("qobuz")
            if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
                self.userA.confirm_auth_dialog()
            assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
                "入口 3:OAuth 外域登录页未出现")
            self.userA.press_back()
            if self.userA.find_text_by_ocr("QQ音乐", timeout=3) is None:
                self.userA.press_back()
            assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
                "入口 3:立即退出后未回到平台页")
            self.userA.assert_no_auth_error()
            ran = True
        if not ran:
            pytest.skip(
                "三入口平台行均非未授权态,取消静默一致性无法发起(账号态自适配)")
        self.userA.assert_no_auth_error()
