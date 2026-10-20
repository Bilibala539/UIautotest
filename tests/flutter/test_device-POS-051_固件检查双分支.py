# CASE-ID: device-POS-051
"""Swan 回归·设备域：固件检查双分支结果断言(device-POS-051)。

步骤→AW 映射：
S1 触发固件检查 → open_device_settings_page + open_firmware_page 后点
   「检查更新」(入口/页未定位时 pytest.skip)；
S2 分支 a(无新版) → 结果文案命中「已是最新/最新版本」时断言提示正确，
   不做升级交互；
S3 分支 b(有新版) → 结果文案命中「发现新版本/新版本」时断言新版信息与
   升级入口「存在性」(OCR 可见即成立)，红线(禁区 1)：升级入口绝不点击。

cleanup: 仅检查无写操作，零升级指令下发。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestFirmwareCheckDualBranch(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_firmware_check_dual_branch(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.open_firmware_page() is None:
            pytest.skip("设备设置页固件/检查更新入口未定位(设置页未探索,需真机标定)")
        if self.userA.probe_any_ocr(("检查更新",), timeout=4) is not None:
            self.userA.click_text("检查更新", timeout=4)
        result = self.userA.probe_any_ocr(("已是最新", "最新版本", "发现新版本", "新版本"),
                                          timeout=15)
        assert result is not None, "固件检查无结果文案(检查未生效或文案未标定)"
        if "最新" in result:
            self.userA.assert_any_ocr(("已是最新", "最新版本"), timeout=6)
        else:
            self.userA.assert_any_ocr(("发现新版本", "新版本"), timeout=6)
            self.userA.assert_any_ocr(("升级", "立即升级", "更新"), timeout=6)

    def teardown(self) -> None:
        pass
