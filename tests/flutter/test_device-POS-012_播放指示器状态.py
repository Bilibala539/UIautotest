# CASE-ID: device-POS-012
"""Swan 回归·设备域：卡片播放动画指示随播放态切换(device-POS-012)。

步骤→AW 映射：
S1/S2 播放态指示 → preset_playing('wifi_device') 后回设备页；动画指示器本体
   为帧序列动效，截图比对基准由执行轮建立(YAML S2 原文，登记 template_needs)；
   OCR 阶段以「绑定真机卡片可见+播放会话存活」守门；
S3 停止播放 → open_player_page + player_control('pause')(App 内暂停，
   强于人工停止口径，自带 assert_paused 收尾)；
S4 指示消失 → press_back 回设备页，断言卡片恢复渲染(机名仍可见；
   动画消失为视觉态归 template_needs)。

cleanup: 播放会话置为暂停态(服务端记忆，后续用例 preset_playing 会重开)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestPlayingIndicatorState(BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_playing_indicator_follows_playback(self):
        self.userA.ensure_logged_in_on_home()
        self.userA.preset_playing("wifi_device")
        self.userA.open_device_page()
        if self.userA.find_text_by_ocr(self.userA.bound_device_name(),
                                       timeout=8,
                                       region=(0, 150, 720, 1150)) is None:
            pytest.skip("绑定真机卡片不可见(设备离线/未绑定),需真机在线预置")
        self.userA.text_exists("连接良好", timeout=6)
        self.userA.open_player_page()
        self.userA.assert_playing()
        self.userA.player_control("pause")
        self.userA.press_back()
        self.userA.text_exists(self.userA.bound_device_name(), timeout=8)

    def teardown(self) -> None:
        pass
