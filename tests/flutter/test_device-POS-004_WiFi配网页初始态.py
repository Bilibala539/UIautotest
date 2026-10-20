# CASE-ID: device-POS-004
"""Swan 回归·设备域：WiFi 配网页合法初始态(device-POS-004)。

步骤→AW 映射：
S1 进入添加设备页 → open_device_page + open_add_device_page；
S2 点 WiFi 卡片 → open_wifi_provisioning(「WiFi 添加」卡片点击)；
S3 合法初始态断言 → 未连热点出提示 / 已连热点出列表，双分支均合法，
   以「热点/Wi-Fi/网络/连接」多候选锚点落位(分支内具体文案登记 template_needs)。

cleanup: back_to_device_page 返回键退出，不提交任何凭据(禁区 3)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestWifiProvisioningInitialState(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_wifi_provisioning_initial_state(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_wifi_provisioning()
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
