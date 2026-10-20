# CASE-ID: device-POS-009
"""Swan 回归·设备域：分区锚点滚动定位(device-POS-009)。

步骤→AW 映射：
S1 设备页列表加载 → open_device_page(锚点=添加设备[图])；
S2/S3 依次点击左侧分区导航锚点并断言右侧列表区滚定至对应分区标题：
   WIFI→WIFI 区标题、本机→扬声器卡、Apple→Apple 分区、低音炮→低音炮分区、
   DSP→DSP 分区；左侧导航与列表区按知识库布局以 region 切分
   (导航 x<140，列表 x∈[140,720))，锚点连点即滚动定位，不卡死即达。
分区文案与布局来自知识库设备页 dump，未覆盖变体登记 template_needs。

cleanup: 无状态变更，纯滚动定位。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestSectionAnchorScroll(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_section_anchor_scroll_positioning(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.click_text("WIFI", timeout=8, region=(0, 150, 140, 1150))
        self.userA.text_exists("WIFI", timeout=8, region=(140, 150, 580, 1150))
        self.userA.click_text("本机", timeout=8, region=(0, 150, 140, 1150))
        self.userA.text_exists("扬声器", timeout=8, region=(140, 150, 580, 1150))
        self.userA.click_text("Apple", timeout=8, region=(0, 150, 140, 1150))
        self.userA.text_exists("Apple", timeout=8, region=(140, 150, 580, 1150))
        self.userA.click_text("低音炮", timeout=8, region=(0, 150, 140, 1150))
        self.userA.text_exists("低音炮", timeout=8, region=(140, 150, 580, 1150))
        self.userA.click_text("DSP", timeout=8, region=(0, 150, 140, 1150))
        self.userA.text_exists("DSP", timeout=8, region=(140, 150, 580, 1150))

    def teardown(self) -> None:
        pass
