# CASE-ID: device-NEG-023
"""Swan 回归·设备域：BLE 权限拒绝引导——按类型跳设置(device-NEG-023)。

步骤→AW 映射：
S1 权限拒绝态点 BLE 卡 → open_add_device_page 后点「蓝牙添加」，探测系统权限
   弹窗并点「不允许/拒绝」拒绝；弹窗未现(权限已授权)时 pytest.skip(拒绝态需
   人工预置)；拒绝后断言 App 内权限引导层出现(非静默失败)；
S2 引导按钮 → 探测「去设置」类控件，命中则点击并断言前台已离开 App
   (get_foreground_package)，press_back 返回；仅命中泛化「设置」文案时不点击，
   只断言引导控件存在(跳转落点断言需真机标定，见 template_needs)；
S3 设置页人工授权后返回 → 授权动作属人工轮次，本用例不代做系统权限写入；
S4 再次拒绝重复一轮 → 会话级授权验证依赖人工授权轮次，如实不执行。

cleanup: back_to_device_page 逐级返回设备页，不改变系统权限状态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestBlePermissionDenyGuide(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_ble_permission_deny_guide(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        self.userA.open_add_device_page()
        hit = self.userA.click_first_ocr(("蓝牙添加", "蓝牙"), timeout=6)
        assert hit is not None, "添加设备页未找到「蓝牙添加」卡片"
        deny = self.userA.click_first_ocr(("不允许", "拒绝", "禁止", "取消"), timeout=6)
        if deny is None:
            self.userA.back_to_device_page()
            pytest.skip("无系统权限弹窗(权限已授权或弹窗未被捕获),"
                        "需权限拒绝态人工预置;S3 授权/S4 复拒为人工轮次")
        self.userA.assert_any_ocr(("权限", "去设置", "开启", "授权"), timeout=8)
        btn = self.userA.click_first_ocr(("去设置", "前往设置", "去开启", "开启权限"), timeout=4)
        if btn is not None:
            fg = self.userA.get_foreground_package()
            assert fg != self.userA.package, f"点击权限引导按钮后未跳离 App(前台={fg})"
            self.userA.press_back()
        else:
            self.userA.assert_any_ocr(("设置",), timeout=4)
        self.userA.back_to_device_page()

    def teardown(self) -> None:
        pass
