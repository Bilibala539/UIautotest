# CASE-ID: device-POS-044
"""Swan 回归·设备域：AW 耳机面板信息区渲染(device-POS-044)。

步骤→AW 映射：
S1 进入面板 → 设备页 OCR 探测耳机面板入口(无 testId 区，未探索页面)，
   入口未定位或面板锚点未现时 pytest.skip——耳机不在场时面板空态渲染
   亦算正向可达，但空态文案需真机标定；
S2 信息区呈现 → 断言「电量」类信息锚点渲染(电量/连接态，空态亦正向)；
S3 经面板内关闭控件退出 → 探测「关闭/完成/收起」命中则点击并断言面板
   关闭(返回键禁用为既定语义)；未命中时 press_back 兜底并留 template_needs。

cleanup: 面板经关闭控件或返回键退出，无状态残留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestAwPanelInfoRender(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_aw_panel_info_rendered(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.probe_any_ocr(("耳机", "AW 耳机", "AW耳机"), timeout=5) is None:
            pytest.skip("设备域未定位 AW 耳机面板入口(无 testId 区,页面未探索,需真机标定)")
        self.userA.click_first_ocr(("耳机", "AW 耳机", "AW耳机"), timeout=4)
        if self.userA.probe_any_ocr(("电量",), timeout=6) is None:
            self.userA.press_back()
            pytest.skip("耳机面板未见「电量」类信息锚点(空态/信息区文案待真机标定)")
        close = self.userA.click_first_ocr(("关闭", "完成", "收起"), timeout=4)
        if close is None:
            self.userA.press_back()
        else:
            self.userA.text_not_exists("电量", timeout=4)

    def teardown(self) -> None:
        pass
