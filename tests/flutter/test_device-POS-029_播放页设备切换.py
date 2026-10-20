# CASE-ID: device-POS-029
"""Swan 回归·设备域：播放页设备切换面板切向绑定真机(device-POS-029)。

步骤→AW 映射(YAML TESTDEV01/SWAN-TEST-BOX01 对应执行环境绑定真机)：
S1/S2 切换面板与列表 → open_player_page 后 select_device(机名,
   via='player')：播放页设备切换入口打开弹层并按机名 OCR 选行
   (自带头部设备名更新断言)；当前输出已是真机时重复切换无意义，
   按运行时状态 pytest.skip；
S3 完成切换 → select_device 内部落位断言；
收尾还原 → open_device_page + select_device('扬声器', via='card')
   切回本机默认输出。

cleanup: 输出还原为扬声器(与初始状态一致)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPlayerDeviceSwitch(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_player_page_device_switch_to_bound(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.open_player_page()
        if self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                       timeout=6,
                                       region=(0, 60, 720, 120)) is not None:
            pytest.skip("播放页头部已是绑定真机名(当前输出即真机),重复切换无意义")
        self.userA.select_device(self.userA.bound_device_name(), via="player")
        self.userA.open_device_page()
        self.userA.select_device("扬声器", via="card")

    def teardown(self) -> None:
        pass
