# CASE-ID: device-POS-050
"""Swan 回归·设备域：固件检查发起与结果呈现——零升级点击(device-POS-050)。

步骤→AW 映射：
S1 固件信息入口 → open_device_settings_page + open_firmware_page
   (多候选入口，未定位时 pytest.skip)，断言当前版本号可读；
S2 触发检查更新 → 点「检查更新」(安全检查类，非真实升级)；
S3 检查结果呈现 → OCR 断言版本比对结果文案(已是最新/发现新版本多候选)；
   红线(禁区 1)：全程零升级点击，绝不触碰任何升级执行控件。

cleanup: 仅检查无写操作，返回键语义由框架冷启动收尾。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestFirmwareCheckZeroUpgrade(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_firmware_check_result_zero_upgrade_click(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.open_firmware_page() is None:
            pytest.skip("设备设置页固件/检查更新入口未定位(设置页未探索,需真机标定)")
        self.userA.assert_any_ocr(("当前版本", "固件版本", "版本"), timeout=8)
        if self.userA.probe_any_ocr(("检查更新",), timeout=4) is not None:
            self.userA.click_text("检查更新", timeout=4)
        self.userA.assert_any_ocr(("已是最新", "最新版本", "发现新版本", "新版本"),
                                  timeout=15)

    def teardown(self) -> None:
        pass
