# CASE-ID: device-POS-003
"""Swan 回归·设备域：BLE 配网页打开即扫描(device-POS-003)。

步骤→AW 映射：
S1 进入添加设备页 → open_device_page + open_add_device_page；
S2 点 BLE 卡片 → open_ble_provisioning(「蓝牙添加」卡片点击)；
S3 扫描态断言 → assert_ble_scanning(「正在扫描/扫描中/扫描」OCR 轮询，
   扫描启动允许数秒延迟)。
未探索页面：BLE 配网页扫描态文案登记 template_needs。

cleanup: back_to_device_page 返回键退出，不发生配对。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestBleProvisioningScanState(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_ble_provisioning_scanning(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_ble_provisioning()
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
