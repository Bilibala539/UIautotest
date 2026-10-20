# CASE-ID: device-NEG-025
"""Swan 回归·设备域：改名空名分支——清空被拒原名保留(device-NEG-025)。

步骤→AW 映射：
S1 改名页可达+预填原名 → open_device_settings_page(设备名行=设置入口[OCR])
   + open_rename_page(改名入口，预填=环境变量 SWAN_DEVICE_NAME 机名)；
S2 清空 → 优先点「清空/清除」控件，无控件则点击输入框聚焦后 clear_input；
   「保存按钮禁用/置灰」为视觉态无法 OCR 断言，以提交行为+零写入替代验证
   (见 report.template_needs 保存按钮双态)；
S3 提交空名 → 点击保存/确定提交观察，端口层应拒绝(禁区 7：空名为非法值，
   不构成合法名写入，可安全提交)；
S4 原名保留 → 返回键退回设备页，卡片区域核对设备名仍为原名。

cleanup: 全程不提交合法名，仅返回键退出，无需恢复动作。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRenameEmptyRejected(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_rename_empty_rejected_keep_original(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if not self.userA.open_rename_page():
            pytest.skip("设备设置页「改名」入口未定位(设置页未探索,需真机标定)")
        if self.userA.click_first_ocr(("清空", "清除"), timeout=4) is None:
            self.userA.click_text(self.userA.bound_device_name(), timeout=4)
            self.userA.clear_input()
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.press_back()
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "返回设备页后原设备名卡片不可见(名称可能被空名污染)"

    def teardown(self) -> None:
        pass
