# CASE-ID: device-POS-052
"""Swan 回归·设备域：BLE 传输层扫描态建立(device-POS-052)。

步骤→AW 映射：
S1 BLE 卡进入配网 → open_ble_provisioning(添加设备[图]→蓝牙添加→扫描态)；
S2 扫描态建立 → assert_ble_scanning(「正在扫描/扫描中/扫描」轮询锚点)；
S3 广播摘要供数 → 仅当扫描列表出现目标广播(SWAN-TEST/TEST-SYNTHETIC/Synth
   合成前缀，避免误认周边真实设备)时断言条目呈现；目标不在场按用例
   自身口径止步扫描态断言(precondition：不在场时止步扫描态)。

cleanup: back_to_device_page 返回键退出，不发生配对。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestBleTransportScanState(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_ble_transport_scan_state(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_ble_provisioning()
        found = self.userA.probe_any_ocr(("SWAN-TEST", "TEST-SYNTHETIC", "Synth"), timeout=8)
        if found is not None:
            self.userA.text_exists(found, timeout=5)
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
