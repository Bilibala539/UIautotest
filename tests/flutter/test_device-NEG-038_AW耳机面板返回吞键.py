# CASE-ID: device-NEG-038
"""Swan 回归·设备域：AW 耳机面板——系统返回键被吞不关面板(device-NEG-038)。

步骤→AW 映射：
S1 进入面板 → 设备页 OCR 探测耳机面板入口(无 testId 区，未探索页面)；
   入口未定位或面板锚点未现时 pytest.skip(需真机标定/耳机在场轮次)；
S2 系统返回键 → press_back 后断言面板锚点(「电量」类面板文案)仍在
   (返回键被吞的可观察代理)；
S3 面板外透明区(barrier)点击 → 需面板遮罩区模板/坐标标定，如实不执行
   (见 report.template_needs 面板 barrier 区)；
S4 面板内关闭按钮退出 → 探测「关闭/完成/收起」控件，命中则点击并断言
   面板锚点消失；未命中时以 press_back 兜底退出并留模板需求。

cleanup: 面板经关闭控件或返回键退出，无状态残留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest

_PANEL_ANCHORS = ("电量",)


class TestAwEarphonePanelBackSwallow(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_aw_panel_back_key_swallowed(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        entry = self.userA.probe_any_ocr(("耳机", "AW 耳机", "AW耳机"), timeout=5)
        if entry is None:
            pytest.skip("设备域未定位 AW 耳机面板入口(无 testId 区,页面未探索,"
                        "需真机标定或耳机在场轮次)")
        self.userA.click_first_ocr(("耳机", "AW 耳机", "AW耳机"), timeout=4)
        if self.userA.probe_any_ocr(_PANEL_ANCHORS, timeout=6) is None:
            self.userA.press_back()
            pytest.skip("点击入口后未见耳机面板锚点(「电量」类文案未现,"
                        "面板结构需真机标定)")
        self.userA.press_back()
        self.userA.assert_any_ocr(_PANEL_ANCHORS, timeout=6)
        close = self.userA.click_first_ocr(("关闭", "完成", "收起"), timeout=4)
        if close is None:
            self.userA.press_back()
        else:
            self.userA.text_not_exists("电量", timeout=4)

    def teardown(self) -> None:
        pass
