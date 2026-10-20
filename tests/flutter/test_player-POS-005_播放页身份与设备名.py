# CASE-ID: player-POS-005
"""Swan 回归·播放器：播放页身份区与设备名一致性（player-POS-005）。

⚠️ 部分转换：步骤3 蓝牙名占位边界（YAML 自标 SKIP-BT：仅蓝牙环境执行）
不纳入本脚本——框架无蓝牙输出能力；坑 5 正向吸收口径同源（该窗口不断言
具体设备名）。

步骤 → AW 映射：
- 步骤1 本机扬声器播放中身份区 → preset_playing("speaker")（内含底栏
  「扬声器」本机输出断言）+ open_player_page() + read_player_title()
  （曲名 OCR 非空；歌手行同 band 由真机标定后补断言）
- 步骤2 切换输出至 rig 音箱 → select_device(rig_device_name(), via="player")
  （设备弹层 OCR 行点击，内部断言页头设备名=目标，设备名与输出路由一致）
- 清理 输出还原本机 → close_full_player() → go_home() → open_device_page() +
  select_device("扬声器", via="card")（设备卡路径含底栏「扬声器」断言）
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestPlayerIdentityAndDeviceName(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """播放页身份区与设备名一致性（POS-005）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_player_identity_and_device_name(self):
        """本机身份区非空 → 切 rig 音箱设备名更新 → 输出还原本机扬声器。"""
        self.userA.preset_playing("speaker")
        # 步骤1：身份区（曲名 OCR 非空；本机输出语义由前置底栏「扬声器」断言背书）
        self.userA.open_player_page()
        title = self.userA.read_player_title()
        assert title, "播放页身份区曲名 OCR 为空（渲染缺失或 band 失准）"
        # 步骤2：切换输出至 rig 音箱，设备名随输出路由更新（页头断言在内部）
        self.userA.select_device(self.userA.rig_device_name(), via="player")
        # 清理：输出还原本机扬声器（设备卡路径含底栏「扬声器」断言）
        self.userA.close_full_player()
        self.userA.go_home()
        self.userA.open_device_page()
        self.userA.select_device("扬声器", via="card")

    def teardown(self) -> None:
        """无用例私有清理（输出已还原本机扬声器）。"""
        pass
