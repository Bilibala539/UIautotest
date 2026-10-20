# CASE-ID: player-POS-028
"""Swan 回归·播放器：UPnP-DLNA 通道输出与订阅驱动 UI 态（player-POS-028）。

⚠️ B 标定项（ADD1 改判）：GENA 订阅建立为协议级观测（框架无 UPnP/GENA
协议栈观测通道——该子断言留 OTHER 注记同源），UI 层可走部分按 OCR 优先
转换：选 DLNA 设备输出→播放态与进度更新（订阅驱动的 UI 表现代理）。
⚠️ 前置依赖：环境变量 SWAN_DLNA_DEVICE_NAME 指向网络内已上线的
UPnP-DLNA 设备名（未配置则运行时 skip，设备需人工预置）。

步骤 → AW 映射：
- 步骤1 选择 UPnP/DLNA 设备作为输出并发起播放 → preset_playing("speaker")
  → open_player_page() + select_device(DLNA 设备名, via="player")（设备弹层
  OCR 行点击）→ start_play(source="favorite", mode="all")
- 步骤2 订阅驱动进度更新（UI 代理）→ assert_playing() + read_player_progress()
  （进度双时间可读且推进证据在 assert_playing 内）
- 步骤3 订阅缓存不伪权威 → 协议级断言未纳入（框架无协议观测通道），
  UI 层以音量行可读为辅助观察未纳入，注记留档
清理：输出切回本机扬声器并停止播放。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestUpnpDlnaOutputSession(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """UPnP-DLNA 通道输出与订阅驱动 UI 态（POS-028，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_upnp_dlna_output_session(self):
        """DLNA 设备输出起播 → 播放态与进度更新（订阅驱动 UI 代理）。"""
        dlna_name = os.environ.get("SWAN_DLNA_DEVICE_NAME", "")
        if not dlna_name:
            pytest.skip("未配置 SWAN_DLNA_DEVICE_NAME（UPnP-DLNA 设备名，"
                        "需人工预置上线）——环境项")
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1：切 DLNA 设备输出并发起播放
        self.userA.select_device(dlna_name, via="player")
        self.userA.start_play(source="favorite", mode="all")
        # 步骤2：订阅驱动进度更新（UI 代理：播放态+进度双时间可读）
        self.userA.assert_playing()
        progress = self.userA.read_player_progress()
        assert progress is not None, "DLNA 输出下读不到进度双时间（订阅链路未驱动 UI？）"
        # 清理：输出切回本机扬声器并停止播放
        self.userA.select_device("扬声器", via="player")
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（输出已切回本机、已停止播放）。"""
        pass
