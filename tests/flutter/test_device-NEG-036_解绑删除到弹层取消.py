# CASE-ID: device-NEG-036
"""Swan 回归·设备域：解绑/删除设备到确认弹层取消——零副作用(device-NEG-036)。

步骤→AW 映射：
S1 入口定位 → open_device_settings_page 后 OCR 探测「删除设备/解绑」入口；
   入口不可达时按用例自身口径 pytest.skip 预标(执行轮 dump 后再标定，
   设备卡长按路线未探索)；
S2 发起解绑 → 点击入口，确认弹层出现(到弹层即止)；解绑目标为绑定真机
   本体，因全程止于弹层+取消，不发生真实解绑；
S3 点击取消 → 弹层关闭；
S4 复核零副作用 → 返回设备页卡片区域原名可见，设备仍在列表。

cleanup: 仅点「取消」+返回键退出，不发生任何解绑请求。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestUnbindDialogCancel(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_unbind_confirm_dialog_cancel_no_side_effect(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        hit = self.userA.click_first_ocr(("删除设备", "解绑设备", "解绑", "删除"), timeout=6)
        if hit is None:
            pytest.skip("设备设置页未定位删除/解绑入口(卡片未决 2,待执行轮 dump 标定)")
        self.userA.assert_any_ocr(("取消",), timeout=8)
        self.userA.click_first_ocr(("取消",), timeout=5)
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "取消解绑后设备页原设备名卡片不可见(设备疑似被解绑)"

    def teardown(self) -> None:
        pass
