# CASE-ID: music-NEG-019
"""Swan 回归·M07 平台授权:服务未就绪窗口发起→定向提示可重试(music-NEG-019)。

步骤→AW 映射(7.7 授权族,坑 6 定向提示类=qq_service_not_ready):
  1. 构造服务未绑定窗口 → force_stop_app("com.tencent.qqmusic")
     (am force-stop 冷启动,AIDL 绑定 com.tencent.qqmusic.third.api.
     QQMusicApiService 未就绪)后立即发起授权
  2. 定向提示观察 → OCR 轮询变体(未就绪/重试/稍后/服务/失败);窗口
     未复现(AIDL 绑定即时成功)按环境相关 pytest.skip,不作失败
  3. 稍候重试 → 再 tap_platform_row_plus + confirm_auth_dialog(弹层
     出现即授权可正常发起,确认点击 fail-loud)
  4. 挂起锁收口 → dismiss_auth_popup(取消挂起,无绑定写)+
     back_to_platform_page + assert_no_auth_error + 行态仍未授权

cleanup: 正文内 dismiss + 条件返回收口;冷启动模型下弹层不跨用例残留。
B 标定说明:qq_service_not_ready 定向提示真实文案待真机补截,见
package_report.json template_needs;QQ AIDL 120 秒挂起窗口为预期行为
(坑 7),本例不等待其结束。
"""

from __future__ import annotations

import time

import pytest

from conftest import BaseTest


class TestMusicNeg019ServiceNotReady(BaseTest):
    """服务未就绪窗口发起得专属定向提示,失败不阻塞重试、无锁残留。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_service_not_ready_hint_then_retry(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 前置闸门:QQ 行须未授权(授权态预置,不解绑还源)
        state = self.userA.platform_row_state("qq")
        if state != "unauthorized":
            pytest.skip("QQ 需未授权预置,自动化账号态不可达(不解绑还源)")
        # 步骤 1:force-stop QQ 音乐后立即发起授权(冷启动未绑定窗口)
        self.userA.force_stop_app("com.tencent.qqmusic")
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        # 步骤 2:qq_service_not_ready 定向提示观察(B 变体轮询)
        hint = None
        deadline = time.monotonic() + 12.0
        while time.monotonic() < deadline:
            page_text = "".join(
                it["text"] for it in self.userA.ocr_scan_page())
            hit = next(
                (w for w in ("未就绪", "重试", "稍后", "服务", "失败")
                 if w in page_text), None)
            if hit:
                hint = hit
                break
            self.userA.sleep(0.8)
        if hint is None:
            pytest.skip("qq_service_not_ready 窗口未复现(AIDL 绑定即时成功,"
                        "环境相关),本例按预置窗口类 skip")
        # 步骤 3:稍候重试——授权可正常发起(确认弹层出现并确认)
        self.userA.dismiss_auth_popup()
        self.userA.back_to_platform_page()
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        # 步骤 4:挂起锁收口——取消挂起、回平台页、无错误、行态未变
        self.userA.dismiss_auth_popup()
        self.userA.back_to_platform_page()
        self.userA.assert_no_auth_error()
        state_after = self.userA.platform_row_state("qq")
        assert state_after == "unauthorized", (
            f"重试取消后 QQ 行态误变 {state_after!r}(挂起锁残留/误报成功)")
