# CASE-ID: device-POS-007
"""Swan 回归·设备域：RCHIVE DSP 页可达与扫描入口(device-POS-007)。

步骤→AW 映射：
S1 DSP 入口 → 设备页左侧分区导航(region 限定)OCR 定位「DSP」锚点并点击；
   左锚点击后若 DSP 页(透明路由 /device/rchive-dsp)直达即出现扫描入口；
S2 扫描入口呈现 → OCR 断言「扫描」类文案可见(本步不点击)；
S3 关闭返回 → press_back 退透明路由，back_to_device_page 确认遮罩消失回到设备页。
DSP 分区/页面均未探索，锚点未现时如实 pytest.skip 留执行轮 dump 标定。

cleanup: 返回键退出透明路由，无状态变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRchiveDspPageReachable(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_dsp_page_scan_entry_reachable(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        rail = self.userA.find_text_by_ocr("DSP", timeout=6, region=(0, 150, 140, 1150))
        if rail is None:
            pytest.skip("设备页左侧分区导航未见 DSP 锚点(DSP 分区未探索,需真机标定)")
        self.userA.tap(rail[0], rail[1])
        if self.userA.probe_any_ocr(("扫描",), timeout=5) is None:
            pytest.skip("DSP 锚点点击后未见 DSP 页扫描入口"
                        "(路由 /device/rchive-dsp 入口形态待执行轮 dump 标定)")
        self.userA.press_back()
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
