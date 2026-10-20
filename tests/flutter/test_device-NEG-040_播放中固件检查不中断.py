# CASE-ID: device-NEG-040
"""Swan 回归·设备域：设备播放中固件检查——检查不中断播放(device-NEG-040)。

步骤→AW 映射：
S1 播放中进设置页 → preset_playing('wifi_device')(绑定真机出声)后
   open_device_page + open_device_settings_page；
S2 发起固件检查 → open_firmware_page 进入固件页(仅检查入口)，点「检查更新」；
   现网无新版本预置时结果分支为「已是最新」，提示断言按分支容忍；
S3 「升级将中断播放」提示 → 仅在检查结果为发现新版本分支断言(坑 12 文案)；
S4 到升级确认入口即止 → 红线(禁区 1)：全程绝不点击任何升级执行控件，
   仅返回键退出固件页；
S5 复查播放 → 返回键回设备页后 open_player_page + assert_playing
   (播放会话服务端记忆，检查流程不打断)。

cleanup: 无升级指令下发，播放会话保持，无恢复动作需求。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestFirmwareCheckDuringPlayback(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_firmware_check_does_not_interrupt_playback(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.preset_playing("wifi_device")
        self.userA.open_device_page()
        if not self.userA.open_device_settings_page():
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        if self.userA.open_firmware_page() is None:
            pytest.skip("设备设置页固件/检查更新入口未定位(设置页未探索,需真机标定)")
        if self.userA.probe_any_ocr(("检查更新",), timeout=4) is not None:
            self.userA.click_text("检查更新", timeout=4)
        result = self.userA.probe_any_ocr(("已是最新", "最新版本", "发现新版本", "新版本"),
                                          timeout=15)
        assert result is not None, "固件检查无结果文案(检查未生效或文案未标定)"
        if "最新" not in result:
            self.userA.assert_any_ocr(("升级将中断播放", "中断播放"), timeout=6)
        self.userA.press_back()
        self.userA.press_back()
        self.userA.open_player_page()
        self.userA.assert_playing()

    def teardown(self) -> None:
        pass
