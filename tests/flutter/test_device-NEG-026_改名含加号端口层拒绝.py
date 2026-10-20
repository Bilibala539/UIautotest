# CASE-ID: device-NEG-026
"""Swan 回归·设备域：设备改名含 + 号被端口层直接拒绝(device-NEG-026)。

步骤→AW 映射：
S1 输入含 + 号合成名 → 改名页(open_device_settings_page+open_rename_page)
   点击输入框聚焦 → clear_input → input_text('TEST+SYNTHETIC-01')，
   OCR 断言输入层接受(字段可见合成名)；
S2 提交保存 → 点保存/确定；「错误提示」文案未探索无法 OCR 锚定，拒绝以
   S3 零写入为实质断言(错误提示文案见 report.template_needs)；
S3 名称核对 → 返回键退回设备页，卡片区域核对仍为原名(端口层拒绝零写入)；
S4 单字符 + 号极端值 → 重聚焦输入框清空后 input_text('+')再次提交，
   同一零写入断言收尾。

cleanup: 全程只提交非法名(端口层拒绝)，不写合法名，返回键退出即复原。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRenamePlusSignRejected(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_rename_plus_sign_rejected(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if not self.userA.open_rename_page():
            pytest.skip("设备设置页「改名」入口未定位(设置页未探索,需真机标定)")
        self.userA.click_text(self.userA.bound_device_name(), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("TEST+SYNTHETIC-01")
        self.userA.assert_any_ocr(("TEST+SYNTHETIC-01", "SYNTHETIC"), timeout=6)
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.click_first_ocr(("TEST+SYNTHETIC-01", "SYNTHETIC"), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("+")
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.press_back()
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "设备页未见原设备名(含+号名可能被写入)"

    def teardown(self) -> None:
        pass
