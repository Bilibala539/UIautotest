# CASE-ID: player-NEG-001
"""Swan 回归·播放器：切回扬声器后播放态真值守卫（player-NEG-001）。

步骤 → AW 映射：
- 步骤1 本机扬声器起播 → preset_playing("speaker")（登录+首页+扬声器输出+
  我喜欢播放全部，收尾含播放态断言）
- 步骤2/3 播放页设备弹层切 Wi-Fi 音箱 → select_device(rig 设备名, via="player")
  （弹层 OCR 行点击，内部断言页头设备名=目标，切换事务 commit）
- 步骤4 立即切回本机扬声器 → select_device("扬声器", via="player")
  （同一弹层立即反向切换，竞态窗口窗口期）
- 步骤5 播放态真值断言 → assert_playing（暂停键 [图]+进度递增双证据，
  不被旧快照覆盖为 paused）

坑 1a 回归面：旧列表 stopped 快照不得覆盖端口本机播放真值。
判定从宽 B：弹层「本机扬声器」行 OCR 文案与立即切回时序需真机标定（纯 OCR
路径，无新增模板依赖）。
清理：结束态=本机扬声器播放中（输出与用例前一致）；冷启动模型 teardown pass。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestOutputSwitchBackPlayingGuard(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """切回扬声器后播放态真值守卫（NEG-001）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_output_switch_back_playing_guard(self):
        """本机起播 → 切 Wi-Fi 音箱 → 立即切回扬声器 → 播放态=playing。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤3：切走输出（commit 完成，页头设备名断言在 select_device 内）
        self.userA.select_device(self.userA.rig_device_name(), via="player")
        # 步骤4：同弹层立即切回本机扬声器（旧快照 vs 端口真值竞态窗口）
        self.userA.select_device("扬声器", via="player")
        # 步骤5：本机播放态端口真值守卫
        self.userA.assert_playing()

    def teardown(self) -> None:
        """无用例私有清理（结束态=本机扬声器播放中，输出与用例前一致）。"""
        pass
