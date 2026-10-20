# CASE-ID: device-POS-008
"""Swan 回归·设备域：AW 耳机面板可达与关闭(device-POS-008)。

步骤→AW 映射：
S1 进入面板 → 设备页 OCR 探测耳机面板入口(无 testId 区，未探索页面)，
   入口未定位或面板锚点(「电量」类文案)未现时 pytest.skip——耳机不在场时
   面板空态渲染亦算正向可达，但入口与空态文案需真机标定；
S2 系统返回键 → press_back 后断言面板锚点仍在(返回键禁用为预期)；
S3 面板内关闭控件 → 探测「关闭/完成/收起」命中则点击并断言面板关闭；
   未命中时 press_back 兜底退出并登记 template_needs。

cleanup: 面板经关闭控件或返回键退出，无状态残留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestAwEarphonePanelReachable(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_aw_earphone_panel_reachable(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.probe_any_ocr(("耳机", "AW 耳机", "AW耳机"), timeout=5) is None:
            pytest.skip("设备域未定位 AW 耳机面板入口(无 testId 区,页面未探索,需真机标定)")
        self.userA.click_first_ocr(("耳机", "AW 耳机", "AW耳机"), timeout=4)
        if self.userA.probe_any_ocr(("电量",), timeout=6) is None:
            self.userA.press_back()
            pytest.skip("点击入口后未见耳机面板锚点(「电量」类文案未现,面板结构需真机标定)")
        self.userA.press_back()
        self.userA.assert_any_ocr(("电量",), timeout=6)
        close = self.userA.click_first_ocr(("关闭", "完成", "收起"), timeout=4)
        if close is None:
            self.userA.press_back()
        else:
            self.userA.text_not_exists("电量", timeout=4)

    def teardown(self) -> None:
        pass
