# CASE-ID: device-NEG-027
"""Swan 回归·设备域：改名超长/emoji/纯空格边界——不真改(device-NEG-027)。

步骤→AW 映射：
S1 超长名(65 字符合成串) → 改名页(open_device_settings_page+open_rename_page)
   聚焦输入框 → clear_input → input_text，点保存提交观察，无静默提交；
S2 emoji 名(Synth音箱📶01) → 重聚焦(按上一轮字段残留 OCR 点击) → 清空 →
   输入 → 提交；emoji 不参与 OCR 断言，主断言不依赖其回显；
S3 纯空格名 → 同上重聚焦清空后 input_text 空格串，trim 后按空名分支拒绝；
S4 名称核对 → 返回键退回设备页，卡片区域核对设备名始终为原名(零写入)。
三组值均非法(超长/非法字符/空名)，提交不构成合法名写入(禁区 7)。

cleanup: 全程只提交非法名，返回键退出即复原，无需恢复动作。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRenameBoundaryValues(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_rename_boundary_values_rejected(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if not self.userA.open_rename_page():
            pytest.skip("设备设置页「改名」入口未定位(设置页未探索,需真机标定)")
        self.userA.click_text(self.userA.bound_device_name(), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("Synth" + "A" * 60)
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.click_first_ocr(("Synth",), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("Synth音箱📶01")
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.click_first_ocr(("音箱", "Synth"), timeout=4)
        self.userA.clear_input()
        self.userA.input_text("      ")
        self.userA.click_first_ocr(("保存", "确定", "完成"), timeout=4)
        self.userA.press_back()
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                           timeout=8,
                                           region=(0, 150, 720, 1150)) is not None, \
            "设备页未见原设备名(边界值名可能被写入)"

    def teardown(self) -> None:
        pass
