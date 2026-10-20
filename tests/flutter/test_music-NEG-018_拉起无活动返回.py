# CASE-ID: music-NEG-018
"""Swan 回归·M07 平台授权:拉起后无活动返回→定向提示不静默(music-NEG-018)。

步骤→AW 映射(7.7 授权族,坑 6 定向提示类=no_activity):
  1. 发起 QQ 授权拉起 QQ 音乐 → platform_row_state 闸门(非未授权即
     skip=YAML 授权态预置)+ tap_platform_row_plus + confirm_auth_dialog
  2. 观察拉起 → foreground_package 轮询 com.tencent.qqmusic(设备级
     只读原语);超时未捕获仍按"拉起尝试已发生"走无活动返回
  3. 无活动立即返回 → back_to_platform_page(条件返回,根级禁盲返)
  4. 定向提示断言 → assert_any_text 变体扫描(无活动/稍后/重试/未完成
     /失败),非静默=提示文案必须出现,与 user_cancel 静默可区分
  5. 收口 → dismiss_auth_popup(取消挂起授权,cancelAuthorize 无绑定写)
     + back_to_platform_page + assert_no_auth_error + 行态仍未授权
     (不误报授权成功、无挂起锁残留)

cleanup: 正文内 dismiss + 条件返回收口;冷启动模型下弹层不跨用例残留。
B 标定说明:no_activity 定向提示真实文案与「授权中」进度弹层文案待真机
补截,见 package_report.json template_needs;QQ AIDL 120 秒挂起窗口为
预期行为(坑 7),本例不等待其结束。
"""

from __future__ import annotations

import time

import pytest

from conftest import BaseTest


class TestMusicNeg018NoActivityReturn(BaseTest):
    """拉起后无活动返回归一 no_activity 并出定向提示(非静默)。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_no_activity_return_directive_hint(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:QQ 行须未授权(授权态预置,不解绑还源)
        state = self.userA.platform_row_state("qq")
        if state != "unauthorized":
            pytest.skip("QQ 需未授权预置,自动化账号态不可达(不解绑还源)")
        # 步骤 1:发起授权拉起 QQ 音乐
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        # 步骤 2:观察 QQ 音乐前台(设备级只读;超时仍按拉起尝试已发生)
        launched = False
        deadline = time.monotonic() + 20.0
        while time.monotonic() < deadline:
            pkg = self.userA.foreground_package()
            if pkg and "qqmusic" in pkg:
                launched = True
                break
            self.userA.sleep(0.8)
        # 步骤 3:无活动立即返回宿主(条件返回,根级禁盲返)
        self.userA.back_to_platform_page()
        # 步骤 4:no_activity 定向提示必须出现(非静默类,文案 B 变体)
        self.userA.assert_any_text(
            ("无活动", "稍后", "重试", "未完成", "失败", "返回"), timeout=8)
        # 步骤 5:收口——取消挂起授权、回平台页、无错误、行态未变
        self.userA.dismiss_auth_popup()
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
        state_after = self.userA.platform_row_state("qq")
        assert state_after == "unauthorized", (
            f"无活动返回后 QQ 行态误变 {state_after!r}(误报授权成功/挂起锁残留)")
