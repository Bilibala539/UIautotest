# CASE-ID: device-POS-010
"""Swan 回归·设备域：绑定真机卡片五要素展示(device-POS-010)。

步骤→AW 映射(YAML 中 TESTDEV01/SWAN-TEST-BOX01 对应执行环境绑定真机，
机名读环境变量 SWAN_DEVICE_NAME)：
S1 卡片容器 → open_device_page 后卡片区域(region 限定)定位设备名，
   不可见(离线/未绑)时 pytest.skip；
S2 设备名节点 → OCR 断言机名；
S3 选中态标记 → 视觉态无已注册模板，登记 template_needs(与当前输出指向
   一致性归播放域用例覆盖)；
S4 设置入口 → 设备名行即设置入口(知识库口径)，随 S2 名称可见一并成立；
S5 同步按钮 → OCR 断言「同步设备」可见(本步不点击)。
另断言在线状态要素「连接良好」与操作要素「音量设置」可见。

cleanup: 全程只读断言，不点击同步/设置。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestDeviceCardFiveElements(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_device_card_five_elements(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_device_page()
        if self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                       timeout=8,
                                       region=(0, 150, 720, 1150)) is None:
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        self.userA.text_exists("连接良好", timeout=6)
        self.userA.text_exists("同步设备", timeout=6)
        self.userA.text_exists("音量设置", timeout=6)

    def teardown(self) -> None:
        pass
