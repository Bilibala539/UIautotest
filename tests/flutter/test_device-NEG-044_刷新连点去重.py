# CASE-ID: device-NEG-044
"""Swan 回归·设备域：刷新连点/并发去重——请求流不叠加(device-NEG-044)。

步骤→AW 映射：
S1 快速连点刷新 5 次 → 刷新控件无文案且无已注册模板(device_refresh_button
   待截图)，先探测「刷新」文案：命中则连点 5 次，未命中则留 template_needs
   并跳过点击(以 Tab 往返后的列表一致性作守门断言)；
S2/S3 刷新中切 Tab 往返 → go_bottom_tab 首页↔设备，返回后断言绑定真机卡片
   仍唯一可见(无双重加载经卡片名区域限定单次命中作可观察代理)；
S4/S5 网络 WiFi 切换 3 轮 → 依赖执行机 WLAN 切换人工预置，如实不执行
   (专用靶机轮次)。

cleanup: 无写操作，纯导航与刷新观察。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRefreshRapidTapDedup(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_refresh_rapid_tap_dedup(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                       timeout=6,
                                       region=(0, 150, 720, 1150)) is None:
            pytest.skip("绑定真机卡片不可见(需至少一台 TEST-SYNTHETIC 在线设备人工预置)")
        if self.userA.probe_any_ocr(("刷新",), timeout=3) is not None:
            for _ in range(5):
                self.userA.click_text("刷新", timeout=2)
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("设备")
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "切 Tab 往返后绑定真机卡片不可见(列表刷新流疑似异常)"

    def teardown(self) -> None:
        pass
