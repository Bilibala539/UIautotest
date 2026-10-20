# CASE-ID: player-NEG-026
"""Swan 回归·播放器：音频焦点抢占中断（场景 A 第三方音频 App）（player-NEG-026）。

⚠️ B 标定项（ADD1 改判）：场景 A（第三方音频 App 抢焦点）框架具备 start_app/
stop_app 通道，可转换（包名经环境变量注入，真机预置项）；场景 B（AI 实时
通话打断，TBD·语义）入口未截取，留 template_needs 待标定。
⚠️ 前置依赖：环境变量 SWAN_FOCUS_PROBE_APP 指向真机上已装的第三方音频
App 包名（未配置则运行时 skip，不判失败）。

步骤 → AW 映射（场景 A）：
- 步骤1 本机起播 → preset_playing("speaker") + open_player_page() + assert_playing()
- 步骤2 启动第三方音乐 App 抢占焦点 → start_external_app(包名)（driver 通道）
  → assert_paused()（本 App 暂停收敛）
- 步骤3 归还焦点（停掉第三方 App）→ stop_external_app(包名) → assert_paused()
  （不越权自动恢复，Dart 无 GAIN 处理）
- 步骤4 用户手动恢复 → player_control("play") + assert_playing()
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestAudioFocusPreemption(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """音频焦点抢占中断——场景 A 第三方音频 App（NEG-026，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_audio_focus_preemption(self):
        """第三方 App 抢焦点 → 本 App 暂停 → 归还不越权恢复 → 手动恢复。"""
        probe_pkg = os.environ.get("SWAN_FOCUS_PROBE_APP", "")
        if not probe_pkg:
            pytest.skip("未配置 SWAN_FOCUS_PROBE_APP（第三方音频 App 包名，"
                        "需真机预置）——场景 A 环境项")
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        self.userA.assert_playing()
        # 步骤2：第三方 App 抢占焦点，本 App 暂停收敛
        self.userA.start_external_app(probe_pkg)
        self.userA.assert_paused()
        # 步骤3：归还焦点（停第三方 App），不越权自动恢复
        self.userA.stop_external_app(probe_pkg)
        self.userA.assert_paused()
        # 步骤4：用户手动恢复
        self.userA.player_control("play")
        self.userA.assert_playing()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放；第三方 App 已停止）。"""
        pass
