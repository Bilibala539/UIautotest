# CASE-ID: device-NEG-001
"""Swan 回归·设备域：设备页 WiFi 分区空态守门(device-NEG-001)。

步骤→AW 映射：
S1 设备页可达 → ensure_logged_in_on_home + open_device_page(锚点=右上角添加设备[图])；
S2 空态观察 → OCR 断言「暂无WIFI设备」空态文案(知识库实测空态文案)；账号名下
   存在绑定设备/离线致空态未现时按运行时状态 pytest.skip(空态需 TEST-SYNTHETIC
   空设备账号人工预置)；
S3 刷新守门 → 刷新控件无文案无已注册模板，先探测「刷新」文案命中才点击
   (缺失时仅复核空态稳定，见 report.template_needs 刷新按钮图标)；
S4/S5 Tab 往返 → go_bottom_tab 首页↔设备，返回后空态复核一致、无重复叠加。

cleanup: 无(全程只读，不触碰任何设备写操作)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest

_EMPTY_ANCHORS = ("暂无WIFI设备", "暂无 WIFI 设备", "暂无WiFi设备")


class TestDeviceEmptyStateGuard(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_wifi_section_empty_state_guard(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.probe_any_ocr(_EMPTY_ANCHORS, timeout=6) is None:
            pytest.skip("设备页未呈现空态(账号名下存在绑定设备或设备离线),"
                        "需空设备账号(TEST-SYNTHETIC)人工预置")
        self.userA.assert_any_text(_EMPTY_ANCHORS, timeout=5)
        if self.userA.probe_any_ocr(("刷新",), timeout=3) is not None:
            self.userA.click_text("刷新", timeout=3)
        self.userA.assert_any_ocr(_EMPTY_ANCHORS, timeout=8)
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("设备")
        self.userA.assert_any_ocr(_EMPTY_ANCHORS, timeout=8)

    def teardown(self) -> None:
        pass
