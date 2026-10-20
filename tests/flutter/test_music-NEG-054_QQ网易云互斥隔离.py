# CASE-ID: music-NEG-054
"""Swan 回归·M07 平台授权:L3 跨平台会话串扰:QQ 挂起×网易云互斥隔离(music-NEG-054)。

步骤→AW 映射(坑 7 单授权锁×坑 1 H5 路径组合面,latest-wins 策略下预期互斥):
  1. 发起 QQ 授权至 AIDL 挂起(进度弹层存活) → tap_platform_row_plus('qq')
     + confirm_auth_dialog(),「取消」钮 [OCR] 探活
  2. 挂起中发起网易云授权 → tap_platform_row_plus('netease',
     template=SWAN_NETEASE_PLUS_BTN),互斥族双口径:auth_in_progress 定向
     提示或挂起被取消后网易云链路放行(确认弹层/H5 登录页)
  3. QQ 取消挂起后发起网易云授权至 H5 → dismiss_auth_popup 清挂起 → 再发起
     至「登录」锚(网易云链路独立可用,无 QQ 挂起残留)
  4. 退出网易云流程,核对两平台授权态 → press_back() 回平台页,
     platform_row_state 双行均为操作前值(未授权)

cleanup: 全部挂起与弹层收束回平台页;服务端态核对走专用账号后置轮;
框架每用例冷启动。
B 标定说明:互斥提示文案未标定(toast 以含「授权」捕获);测试账号已授权
网易云为环境常态,该前置不满足时整例自适配跳过(不做取消授权破坏性操作)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_NETEASE_PLUS_BTN


class TestMusicNeg054CrossPlatformMutex(BaseTest):
    """QQ 挂起×网易云互斥隔离:单授权锁互斥、取消释放、平台态隔离。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_netease_mutex_isolation(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "unauthorized":
            pytest.skip("QQ 行非未授权态,授权挂起链路无法从 [+] 发起(账号态自适配)")
        if self.userA.platform_row_state("netease") != "unauthorized":
            pytest.skip(
                "网易云行非未授权态(测试账号已授权网易云为环境常态),"
                "互斥发起无第二入口(账号态自适配)")
        # 步骤 1:QQ 挂起建立,进度弹层存活
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
            "确认后授权进度弹层未出现(挂起未建立)")
        # 步骤 2:挂起中发起网易云,互斥族双口径二者必居其一
        self.userA.tap_platform_row_plus("netease", template=SWAN_NETEASE_PLUS_BTN)
        mutex_hint = self.userA.wait_toast("授权", timeout=4)
        if not mutex_hint:
            if self.userA.find_text_by_ocr("确认", timeout=6) is not None:
                self.userA.confirm_auth_dialog()
            assert self.userA.find_text_by_ocr("登录", timeout=20) is not None, (
                "挂起中跨平台发起既无互斥提示也未放行网易云链路")
            self.userA.press_back()
        # 步骤 3:QQ 取消挂起后网易云链路独立可用
        self.userA.dismiss_auth_popup()
        self.userA.tap_platform_row_plus("netease", template=SWAN_NETEASE_PLUS_BTN)
        if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
            self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
            "QQ 取消挂起后网易云 H5 授权页未出现(疑挂起残留影响)")
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
            "退出网易云流程后未回到平台页")
        # 步骤 4:两平台授权态均为操作前值(未授权),互不串扰
        self.userA.assert_no_auth_error()
        assert self.userA.platform_row_state("qq") == "unauthorized", (
            "QQ 授权态被网易云流程串扰(应保持未授权)")
        assert self.userA.platform_row_state("netease") == "unauthorized", (
            "网易云授权态漂移(应保持未授权)")
