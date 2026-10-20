# CASE-ID: device-POS-032
"""Swan 回归·设备域：网络设置页当前网络信息(device-POS-032)。

步骤→AW 映射：
S1 入口 → open_device_settings_page 后点「网络设置」(多候选点击，
   入口未定位时 pytest.skip 留真机标定)；
S2 网络信息 → 断言 SSID/信号/Wi-Fi/网络类信息文案渲染(只读不写，
   不触碰任何网络配置)。

cleanup: 返回键退出子页回设置页，无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestNetworkSettingsPage(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_network_settings_page_info(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.click_first_ocr(("网络设置", "网络"), timeout=6) is None:
            pytest.skip("设备设置页「网络设置」入口未定位(设置页未探索,需真机标定)")
        self.userA.assert_any_ocr(("SSID", "信号", "Wi-Fi", "WiFi", "网络"), timeout=8)
        self.userA.press_back()
        self.userA.press_back()

    def teardown(self) -> None:
        pass
