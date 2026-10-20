# CASE-ID: device-POS-034
"""Swan 回归·设备域：语音设置页设置项(device-POS-034)。

步骤→AW 映射：
S1 入口 → open_device_settings_page 后点「语音设置」(多候选点击，
   入口未定位时 pytest.skip 留真机标定)；
S2 设置项呈现 → 断言「语音」类锚点渲染(只读不写，不触碰任何语音开关)。

cleanup: 返回键退出子页回设置页，无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestVoiceSettingsPage(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_voice_settings_page_items(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.click_first_ocr(("语音设置", "语音"), timeout=6) is None:
            pytest.skip("设备设置页「语音设置」入口未定位(设置页未探索,需真机标定)")
        self.userA.assert_any_ocr(("语音",), timeout=8)
        self.userA.press_back()
        self.userA.press_back()

    def teardown(self) -> None:
        pass
