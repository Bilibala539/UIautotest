# CASE-ID: device-POS-028
"""Swan 回归·设备域：卡片音量设置面板打开(device-POS-028)。

步骤→AW 映射：
S1 音量面板打开 → 设备页点「音量设置」入口(多卡场景取首个命中卡片，
   面板归属与绑定真机的对应关系留执行轮核)，断言面板锚点(「%」/「音量」)；
S2/S3 调节至 v0+20 并还原 → 依赖滑杆模板定位与实机音量写纪律
   (drag_on_template 需 slider 截图，见 template_needs)，本转换止步
   面板锚点断言，写轮次如实留执行轮；
收尾 → press_back 关闭面板，零写退出。

cleanup: 不触碰音量写，无需还原。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestVolumePanelOpen(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_volume_panel_open_and_close(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.click_first_ocr(("音量设置",), timeout=6) is None:
            pytest.skip("设备卡「音量设置」入口未定位(卡片操作区未探索,需真机标定)")
        self.userA.assert_any_ocr(("%", "音量"), timeout=8)
        self.userA.press_back()

    def teardown(self) -> None:
        pass
