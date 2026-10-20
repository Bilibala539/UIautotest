# CASE-ID: device-NEG-031
"""Swan 回归·设备域：恢复出厂到弹窗取消——不复位(device-NEG-031)。

步骤→AW 映射：
S1 入口行定位 → open_device_settings_page(设备名行=设置入口[OCR])后 OCR 断言
   「恢复出厂」入口行可见；
S2 点击入口行 → 系统确认弹窗出现(到弹窗即止，本用例终点)；
S3 双按钮语义 → OCR 断言「取消」与「确认/确定/重置」并存；
S4 点击取消 → 弹窗关闭，设置页入口行仍在；
S5 设备无损 → 返回设备页，卡片区域原名可见(名称/在线态未复位)。

cleanup: 仅点「取消」+返回键退出，绝不触碰确认按钮，无恢复动作需求。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestFactoryResetDialogCancel(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_factory_reset_dialog_cancel_no_reset(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        self.userA.assert_any_ocr(("恢复出厂", "恢复出厂设置"), timeout=6)
        self.userA.click_first_ocr(("恢复出厂", "恢复出厂设置"), timeout=6)
        self.userA.assert_any_ocr(("取消",), timeout=8)
        self.userA.assert_any_ocr(("确认", "确定", "重置"), timeout=4)
        self.userA.click_first_ocr(("取消",), timeout=5)
        self.userA.assert_any_ocr(("恢复出厂",), timeout=8)
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "取消恢复出厂后设备页原设备名卡片不可见(设备状态疑似被复位)"

    def teardown(self) -> None:
        pass
