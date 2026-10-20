# CASE-ID: music-POS-039
"""Swan 回归·M07 平台授权:网易云授权至跳转发起·深链/H5 双通道(music-POS-039)。

步骤→AW 映射(7.7 授权族,禁区 1:止于跳转发起/WebView 打开,不输凭据):
  1. 网易云行 [+] 钮 → platform_row_state 闸门(非未授权即 skip=YAML
     授权态预置,不解绑还源)+ tap_platform_row_plus → 授权确认底部弹层
  2. 弹层确认 → confirm_auth_dialog → 设备态二分支:
     - 已装深链:foreground_package 轮询 com.netease.cloudmusic 前台
     - 未装 H5:宿主内 WebView/授权中进度(observe_auth_launch 观察,
       网易云未装不跳商店,两分支均安全)
  3. 未输入任何凭据关闭授权页 → dismiss_auth_popup(取消收束,
     cancelAuthorize 无服务端绑定写)+ back_to_platform_page(条件返回)
  4. 收口断言 → 行态仍未授权(授权流程以取消收尾)+ assert_no_auth_error
     (无崩溃:行态可读即宿主存活)

cleanup: 正文内取消收束;未完成第三方确认即无 op=0 绑定写。
B 标定说明:网易云授权中进度弹层文案与 H5 WebView 形态锚待真机补截,
见 package_report.json template_needs。
"""

from __future__ import annotations

import time

import pytest

from conftest import BaseTest


class TestMusicPos039NeteaseAuthLaunch(BaseTest):
    """网易云授权确认→深链/H5 双通道跳转发起→取消收束主链路可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_auth_to_launch(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:网易云行须未授权(授权态预置,不解绑还源)
        state = self.userA.platform_row_state("netease")
        if state != "unauthorized":
            pytest.skip("网易云需未授权预置,自动化账号态不可达(不解绑还源)")
        # 步骤 1:授权确认弹层出现并确认
        self.userA.tap_platform_row_plus("netease")
        self.userA.confirm_auth_dialog()
        # 步骤 2:设备态二分支观察(深链前台 / 宿主内 H5/授权中)
        launched = False
        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            pkg = self.userA.foreground_package()
            if pkg and "netease" in pkg:
                launched = True
                break
            self.userA.sleep(0.8)
        if not launched:
            # 未装分支:H5 WebView(宿主内授权中进度/网页形态)
            self.userA.observe_auth_launch(max_wait=8.0)
        # 步骤 3-4:未输入凭据,取消收尾回平台页,无崩溃无绑定写
        self.userA.dismiss_auth_popup()
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
        state_after = self.userA.platform_row_state("netease")
        assert state_after == "unauthorized", (
            f"取消收尾后网易云行态误变 {state_after!r}(未输凭据不应绑定)")
