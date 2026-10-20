# CASE-ID: music-POS-040
"""Swan 回归·M07 平台授权:酷狗授权至跳转发起(music-POS-040)。

步骤→AW 映射(7.7 授权族,SDK UltimateWiFi 拉起,发起即止):
  1. 酷狗行 [+] 钮 → platform_row_state 闸门(非未授权即 skip=YAML 授权态
     预置)+ tap_platform_row_plus → 授权确认底部弹层
  2. 弹层确认 → confirm_auth_dialog → SDK 拉起授权发起
  3. 进度弹层/第三方拉起双形态 → observe_auth_launch → 进度弹层可取消

cleanup: 进度弹层点取消还原。写风险声明:酷狗授权发起触发 SDK 侧设备
激活记录写(UltimateWiFi init+device/activation),仅限专用测试账号执行
(账号不可写时整例 SKIP-AUTH-WRITE,此处以行授权态闸门自适配);激活
记录还原归专用解绑轮,本例不做(禁区 2/4),不触达 kugou/activation 换票。
B 标定说明:kugou_auth_bg 弹层背景图与进度弹层文案待真机补截,见
package_report.json template_needs。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos040KugouAuthLaunch(BaseTest):
    """酷狗授权弹层→SDK 拉起发起→取消收束主链路可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_kugou_auth_to_launch(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:酷狗行须未授权(授权态预置;账号不可写=SKIP-AUTH-WRITE)
        state = self.userA.platform_row_state("kugou")
        if state != "unauthorized":
            pytest.skip(
                f"酷狗行授权态={state}(YAML 需未授权预置;SDK 激活记录写"
                "仅限专用账号,禁止对基线账号解绑还源)")
        # 步骤 1:[+] 钮 → 授权确认底部弹层
        self.userA.tap_platform_row_plus("kugou")
        self.userA.assert_any_text(["确认", "授权"])
        # 步骤 2:确认 → SDK 拉起授权发起
        self.userA.confirm_auth_dialog()
        # 步骤 3:进度弹层或第三方拉起(双形态),条件返回后弹层可取消
        self.userA.observe_auth_launch()
        self.userA.dismiss_auth_popup()
        self.userA.text_not_exists("授权中", timeout=3)
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
