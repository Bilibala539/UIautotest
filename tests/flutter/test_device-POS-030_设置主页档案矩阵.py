# CASE-ID: device-POS-030
"""Swan 回归·设备域：设备设置主页档案与入口矩阵(device-POS-030)。

步骤→AW 映射：
S1 设置入口 → open_device_settings_page(设备名行=设置入口[OCR])；
S2 档案加载 → 断言设备名可见，IP/型号/MAC/设备信息字段至少其一渲染
   (字段文案未探索，多候选容忍，具体字段登记 template_needs)；
S3 设置族入口矩阵 → 断言「改名」「网络设置」「恢复出厂」三类入口可见
   (代表子集，全矩阵见 template_needs)；入口可点性由后续子页用例覆盖。

cleanup: 只读断言，停留设置页无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestDeviceSettingsHome(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_device_settings_profile_and_entries(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        self.userA.assert_any_ocr((self.userA.bound_device_name(),), timeout=6)
        self.userA.assert_any_ocr(("IP", "型号", "MAC", "设备信息"), timeout=8)
        self.userA.assert_any_ocr(("改名", "重命名", "设备名称"), timeout=6)
        self.userA.assert_any_ocr(("网络设置", "网络"), timeout=6)
        self.userA.assert_any_ocr(("恢复出厂",), timeout=6)

    def teardown(self) -> None:
        pass
