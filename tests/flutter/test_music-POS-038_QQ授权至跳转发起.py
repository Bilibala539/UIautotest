# CASE-ID: music-POS-038
"""Swan 回归·M07 平台授权:QQ授权至跳转发起(music-POS-038)。

步骤→AW 映射(7.7 授权族,禁区 1:止于跳转发起,不输第三方凭据):
  1. QQ 行 [+] 钮 → platform_row_state 闸门(非未授权即 skip=YAML 授权态
     预置,不解绑还源)+ tap_platform_row_plus → 授权确认底部弹层
  2. 弹层确认 → confirm_auth_dialog → 意图/AIDL 绑定发起
  3-4. 进度弹层/第三方拉起双形态 → observe_auth_launch(第三方前台条件
     返回一次)→ dismiss_auth_popup 取消进度弹层(cancelAuthorize→
     user_cancel,无服务端绑定写)→ 回平台页无错误文案

cleanup: 进度弹层点取消收束;未完成第三方确认即无 op=0 绑定写。
B 标定说明:qq_auth_bg legacy 弹层背景图与授权中进度弹层文案(runWith
PlatformAuthProgress)待真机补截,见 package_report.json template_needs。
坑 7:QQ AIDL 授权 120 秒挂起窗口为预期行为,本例不等待其结束。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos038QqAuthLaunch(BaseTest):
    """QQ 授权弹层→跳转发起→取消收束主链路可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_auth_to_launch(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:QQ 行须未授权(授权态预置,不解绑还源)
        state = self.userA.platform_row_state("qq")
        if state != "unauthorized":
            pytest.skip(
                f"QQ 行授权态={state}(YAML 需未授权预置;"
                "账号级绑定写禁区,禁止解绑还源)")
        # 步骤 1:[+] 钮 → 授权确认底部弹层
        self.userA.tap_platform_row_plus("qq")
        self.userA.assert_any_text(["确认", "授权"])
        # 步骤 2:确认 → 意图/AIDL 绑定发起
        self.userA.confirm_auth_dialog()
        # 步骤 3/4:进度弹层或第三方拉起(双形态),条件返回后弹层可取消
        self.userA.observe_auth_launch()
        self.userA.dismiss_auth_popup()
        self.userA.text_not_exists("授权中", timeout=3)
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
