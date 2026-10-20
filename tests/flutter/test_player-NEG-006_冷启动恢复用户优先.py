# CASE-ID: player-NEG-006
"""Swan 回归·播放器：冷启动恢复与用户选择竞态（用户优先）（player-NEG-006）。

步骤 → AW 映射：
- 前置 遗留 Wi-Fi 音箱输出会话 → preset_playing("wifi_device")（播放会话
  持久化，relaunch 不清，lastDeviceUUID 生效）
- 步骤1 冷启动观察自动恢复 → restart_app()（relaunch 内置首页锚断言，
  恢复事务随持久会话自动启动）
- 步骤2 恢复事务进行中立即手动选择本机扬声器 → open_device_page() +
  select_device("扬声器", via="card")（设备卡 OCR 路径，用户选择优先）
- 步骤3 终态归属断言 → select_device 内部底栏「扬声器」OCR 断言（无双重提交）
- 步骤4 播放功能可用性 → start_play(source="favorite", mode="all") + assert_playing

supersedePendingRestore 回归面：用户选择优先于恢复事务、无双重提交、
无展示闪烁死循环。
清理：结束态=本机扬声器播放中（输出已还原）；teardown pass。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestColdStartRestoreUserPriority(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """冷启动恢复与用户选择竞态（用户优先）（NEG-006）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_restore_user_priority(self):
        """遗留 Wi-Fi 会话冷启动 → 恢复事务中手动切本机扬声器 → 用户优先。"""
        # 前置：制造「上次会话遗留 Wi-Fi 音箱输出」持久会话
        self.userA.preset_playing("wifi_device")
        # 步骤1：冷启动（恢复事务随持久会话自动启动）
        self.userA.restart_app()
        # 步骤2/3：恢复窗口期立即手动切本机扬声器（用户选择优先、终态归属）
        self.userA.open_device_page()
        self.userA.select_device("扬声器", via="card")
        # 步骤4：播放功能可用性（输出归属=本机）
        self.userA.start_play(source="favorite", mode="all")
        self.userA.assert_playing()

    def teardown(self) -> None:
        """无用例私有清理（结束态=本机扬声器播放中，输出已还原）。"""
        pass
