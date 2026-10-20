# CASE-ID: player-POS-036
"""Swan 回归·播放器：冷启动输出恢复主路径（player-POS-036）。

步骤 → AW 映射：
- 步骤1 TESTDEV01 播放中杀掉 App 进程 → preset_playing("wifi_device")（rig
  设备端自然续播，用例不碰设备端）+ restart_app()（relaunch 杀进程重启）
- 步骤2 重启进首页，mini 条首帧即有歌 → restart_app 内置首页锚 +
  assert_bottom_bar_session(True, device=rig 设备名)（band 出现 rig 签名行=
  恢复链执行，首帧即有歌，无空白窗口）
- 步骤3 恢复后展示一致性 → click_bottom_player_bar() + open_player_page() +
  assert_playing()（输出恢复 rig，会话与设备端一致）

冷启动输出恢复主路径回归面：lastDeviceUUID 命中，输出与设备态一致。
清理：App 内停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestColdStartOutputRestore(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """冷启动输出恢复主路径（POS-036）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_output_restore(self):
        """rig 播放中杀进程重启 → mini 条首帧有歌 → 输出恢复一致。"""
        # 步骤1：rig 播放中杀掉 App 进程（设备端自然续播仅观测）
        self.userA.preset_playing("wifi_device")
        self.userA.restart_app()
        # 步骤2：重启进首页，mini 条首帧即有歌（rig 签名行在 band）
        self.userA.assert_bottom_bar_session(True, device=self.userA.rig_device_name())
        # 步骤3：恢复后展示一致性（全屏页打开+播放态=会话与设备端一致）
        self.userA.click_bottom_player_bar()
        self.userA.open_player_page()
        self.userA.assert_playing()
        # 清理：App 内停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
