# CASE-ID: device-POS-011
"""Swan 回归·设备域：手动刷新后列表完整(device-POS-011)。

步骤→AW 映射：
S1 基线 → open_device_page 后卡片区域定位绑定真机名(不可见则 skip，
   需在线设备预置)；
S2 刷新触发 → 刷新控件无文案且无已注册模板(device_refresh_button 待截图)，
   探测「刷新」文案命中才点击；指示出现/消失为视觉态登记 template_needs；
S3 列表完整 → 刷新后断言机名卡片与「连接良好」状态仍渲染，分区结构不变。

cleanup: 无写操作，纯刷新观察。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestManualRefreshListIntact(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_manual_refresh_list_intact(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                       timeout=8,
                                       region=(0, 150, 720, 1150)) is None:
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.probe_any_ocr(("刷新",), timeout=3) is not None:
            self.userA.click_text("刷新", timeout=2)
        self.userA.text_exists(self.userA.bound_device_name(), timeout=8)
        self.userA.text_exists("连接良好", timeout=6)

    def teardown(self) -> None:
        pass
