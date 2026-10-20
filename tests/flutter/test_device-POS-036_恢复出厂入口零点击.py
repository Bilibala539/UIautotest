# CASE-ID: device-POS-036
"""Swan 回归·设备域：恢复出厂入口行可见——全程零点击(device-POS-036)。

步骤→AW 映射：
S1 入口行定位 → open_device_settings_page(设备名行=设置入口[OCR])后
   OCR 断言「恢复出厂」入口行可见可辨识；
S2 红线声明 → 全程零点击：除导航定位外不发生任何交互，弹窗零接触
   (复位写操作仅限专用靶机轮次)。

cleanup: 只读断言，无任何点击。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestFactoryResetEntryReadOnly(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_factory_reset_entry_visible_zero_click(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        self.userA.assert_any_ocr(("恢复出厂", "恢复出厂设置"), timeout=8)

    def teardown(self) -> None:
        pass
