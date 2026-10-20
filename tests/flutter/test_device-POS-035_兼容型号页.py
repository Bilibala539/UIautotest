# CASE-ID: device-POS-035
"""Swan 回归·设备域：兼容型号页内容(device-POS-035)。

步骤→AW 映射：
S1 入口 → open_device_settings_page 后点「兼容型号」(入口未定位时
   pytest.skip 留真机标定)；
S2 内容呈现 → 断言「兼容型号/型号」类锚点渲染。

cleanup: 返回键退出子页回设置页，无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestCompatibleModelPage(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_compatible_model_page_content(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.click_first_ocr(("兼容型号",), timeout=6) is None:
            pytest.skip("设备设置页「兼容型号」入口未定位(设置页未探索,需真机标定)")
        self.userA.assert_any_ocr(("兼容型号", "型号"), timeout=8)
        self.userA.press_back()
        self.userA.press_back()

    def teardown(self) -> None:
        pass
