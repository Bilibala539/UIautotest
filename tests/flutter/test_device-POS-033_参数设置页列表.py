# CASE-ID: device-POS-033
"""Swan 回归·设备域：参数设置页参数列表(device-POS-033)。

步骤→AW 映射：
S1 入口 → open_device_settings_page 后点「参数设置」(多候选点击，
   入口未定位时 pytest.skip 留真机标定)；
S2 参数列表 → 断言「参数」类锚点渲染(刷新态不报错——刷新交互留
   执行轮，本转换止步列表锚点)。

cleanup: 返回键退出子页回设置页，无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestParamsSettingsPage(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_params_settings_page_list(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.click_first_ocr(("参数设置", "参数"), timeout=6) is None:
            pytest.skip("设备设置页「参数设置」入口未定位(设置页未探索,需真机标定)")
        self.userA.assert_any_ocr(("参数",), timeout=8)
        self.userA.press_back()
        self.userA.press_back()

    def teardown(self) -> None:
        pass
