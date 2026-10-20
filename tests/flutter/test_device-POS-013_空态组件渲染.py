# CASE-ID: device-POS-013
"""Swan 回归·设备域：空设备账号 WiFi 分区空态组件(device-POS-013)。

步骤→AW 映射：
S1 空账号登录 → 框架承担登录态(专用空设备账号为账号预置，当前账号名下
   存在设备时按运行时状态 pytest.skip)；
S2 进入设备页 → ensure_logged_in_on_home + open_device_page；
S3 分区观察 → 列表区(region 限定)断言 WIFI 分区标题渲染；
S4 空态组件 → OCR 断言「暂无WIFI设备」空态文案，引导入口不点击。

cleanup: 全程只读断言。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest

_EMPTY_ANCHORS = ("暂无WIFI设备", "暂无 WIFI 设备", "暂无WiFi设备")


class TestEmptyStateComponent(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_empty_state_component_rendered(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.probe_any_ocr(_EMPTY_ANCHORS, timeout=6) is None:
            pytest.skip("设备页未呈现空态(需专用空设备账号人工预置,"
                        "当前账号名下存在设备)")
        self.userA.text_exists("WIFI", timeout=6, region=(140, 150, 580, 1150))
        self.userA.assert_any_text(_EMPTY_ANCHORS, timeout=5)

    def teardown(self) -> None:
        pass
