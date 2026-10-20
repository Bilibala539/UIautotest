# CASE-ID: device-NEG-021
"""Swan 回归·设备域：扫描中切页/进详情——停扫生效不叠加(device-NEG-021)。

步骤→AW 映射：
S1 扫描态确认 → open_ble_provisioning(添加设备[图]→蓝牙添加卡片→扫描态 OCR)；
S2 扫描中切 Tab → go_bottom_tab 首页(离开配网页，扫描随页面退出终止)；
S3 返回重进 → 重新 open_ble_provisioning，扫描态再次出现(重置无叠加以
   「扫描态可复现」为可观察代理，双扫描流无法经 OCR 直接观测)；
S4 进入已发现设备详情 → 仅当扫描列表出现合成广播源(SWAN-TEST/TEST-SYNTHETIC/
   Synth 前缀)才点击，避免误触真实周边设备；无广播源时 pytest.skip；
S5 返回列表一致 → press_back 回配网页，列表仍含该设备名。

cleanup: back_to_device_page 逐级返回设备页，全程不发生配对/写入。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestScanStopOnTabSwitch(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_scan_stop_on_tab_switch_no_overlay(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_ble_provisioning()
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("设备")
        self.userA.open_ble_provisioning()
        found = self.userA.probe_any_ocr(("SWAN-TEST", "TEST-SYNTHETIC", "Synth"), timeout=8)
        if found is None:
            self.userA.back_to_device_page()
            pytest.skip("扫描列表无已发现合成广播源(需 TEST-SYNTHETIC 广播源预置),"
                        "S4 进入详情/S5 列表一致性跳过")
        self.userA.click_text(found, timeout=5)
        self.userA.assert_any_ocr((found, "配对", "连接", "下一步"), timeout=8)
        self.userA.press_back()
        self.userA.assert_any_ocr((found,), timeout=8)
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
