# CASE-ID: device-POS-031
"""Swan 回归·设备域：改名页三分支校验与零写入(device-POS-031)。

步骤→AW 映射(YAML SWAN-TEST-BOX01 对应执行环境绑定真机机名)：
S1 改名页可达+预填 → open_device_settings_page + open_rename_page
   (预填=环境变量机名，内置断言)；
S4 输入含 + 号名(SWAN+TEST) → 聚焦输入框 clear 后 input_text，
   OCR 断言输入层接受；
S5 含 + 号提交被拒 → 点保存，拒绝以零写入为实质断言(错误文案待标定)；
S6 合法形态名(SWAN-TEST-RENAMED)仅输入不提交 → 重聚焦清空后录入并
   OCR 断言可录入；
S3 空名提交被拒 → 再次重聚焦清空后点保存(空名提交，端口层拒绝，
   禁区 7：不构成合法名写入)；
S7/S8 返回不保存+零变更 → press_back 退改名页，重进改名页预填仍为
   原名(open_rename_page 内置断言)，退回设备页卡片名核对。

cleanup: 全程只提交非法名(空名/含+号)，合法形态名仅录入不提交，
零写入无需还原。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRenameThreeBranchNoWrite(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_rename_three_branch_zero_write(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if not self.userA.open_rename_page():
            pytest.skip("设备设置页「改名」入口未定位(设置页未探索,需真机标定)")
        self.userA.click_text(self.userA.bound_device_name(), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("SWAN+TEST")
        self.userA.assert_any_ocr(("SWAN+TEST", "TEST"), timeout=6)
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.click_first_ocr(("SWAN+TEST", "TEST"), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("SWAN-TEST-RENAMED")
        self.userA.assert_any_ocr(("SWAN-TEST-RENAMED", "RENAMED"), timeout=6)
        self.userA.click_first_ocr(("RENAMED",), timeout=4)
        self.userA.clear_input()
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.press_back()
        if not self.userA.open_rename_page():
            pytest.skip("返回设置页后「改名」入口不可复入(页面结构待真机标定)")
        self.userA.press_back()
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "设备页未见原设备名(改名页发生了意外写入)"

    def teardown(self) -> None:
        pass
