# CASE-ID: device-POS-027
"""Swan 回归·设备域：输出设备切回本机扬声器(device-POS-027)。

步骤→AW 映射(YAML TESTDEV01 对应执行环境绑定真机)：
S1 基线 → 设备页底部播放条区域 OCR 确认当前输出为绑定真机(机名可见)；
   输出已是扬声器时无可切回，按运行时状态 pytest.skip；
S2/S3 切回本机 → select_device('扬声器', via='card')(本机输出卡片点击，
   自带电池优化弹窗「忽略」处理与贴底播放条「扬声器」断言，
   即选中态还原断言)。

cleanup: 终态即本机扬声器(默认输出)，无需还原。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestSwitchBackToSpeaker(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_switch_output_back_to_speaker(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                       timeout=6,
                                       region=(0, 1360, 720, 130)) is None:
            pytest.skip("底部播放条未见绑定真机名(当前输出非真机),切回本机前置不成立")
        self.userA.select_device("扬声器", via="card")

    def teardown(self) -> None:
        pass
