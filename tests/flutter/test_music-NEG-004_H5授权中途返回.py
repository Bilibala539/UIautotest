# CASE-ID: music-NEG-004
"""Swan 回归·M07 平台授权:网易云 H5 授权页中途系统返回:静默收束(music-NEG-004)。

步骤→AW 映射:
  1. 平台页网易云行点 [+] 发起授权(未安装态走 H5 OAuth WebView,坑 1 授权
     服务族) → tap_platform_row_plus('netease', template=SWAN_NETEASE_PLUS_BTN)
  2. H5 外域登录页出现(禁区 1:断言止于登录页出现,不输入任何凭据)
     → find_text_by_ocr('登录') 有界探测
  3. H5 登录页按系统返回中途退出 → press_back()(WebView 关闭回发起页)
  4. 平台页无错误 toast → assert_no_auth_error()(user_cancel 静默类,坑 6);
     回到平台页以其它平台行「QQ音乐」[OCR] 锚定(H5 登录页无此文案)
  5. 网易云授权态仍为未授权 → platform_row_state('netease')

cleanup: 中途返回后 WebView 已关,无残留弹层即不再动作(根级禁返回键,
不做无弹层盲退);框架每用例冷启动。
B 标定说明:网易云 H5 外域登录页内容未截模板,登录页锚用通用文案「登录」;
真机补截后可收紧为页面专属锚(见 package_report.json template_needs)。
测试账号已授权网易云为环境常态(恒满足),已授权行无 [+] 钮,H5 授权无法
发起,按账号态自适配跳过(不做取消授权的破坏性操作,见批次拍板)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_NETEASE_PLUS_BTN


class TestMusicNeg004H5AuthMidBack(BaseTest):
    """网易云 H5 授权中途返回:user_cancel 静默收束,授权态不变。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_h5_mid_back_silent(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("netease") != "unauthorized":
            pytest.skip(
                "网易云行非未授权态(测试账号已授权网易云为环境常态),"
                "H5 授权无法从 [+] 发起(账号态自适配)")
        self.userA.tap_platform_row_plus("netease", template=SWAN_NETEASE_PLUS_BTN)
        if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
            self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
            "发起后 25s 内未出现 H5 外域登录页(「登录」锚未命中,"
            "WebView 未拉起或加载失败)")
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
            "中途返回后未回到平台页(WebView 未关闭或停留在中间页)")
        self.userA.assert_no_auth_error()
        assert self.userA.platform_row_state("netease") == "unauthorized", (
            "中途返回后网易云授权态发生变化(应保持未授权)")
