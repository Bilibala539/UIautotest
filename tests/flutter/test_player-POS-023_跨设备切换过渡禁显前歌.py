# CASE-ID: player-POS-023
"""Swan 回归·播放器：跨设备切换 Switching 过渡禁显前歌（player-POS-023）。

⚠️ 部分转换：步骤2 过渡期 mini 条「设备名+空」为 Switching 瞬态，OCR 轮询
窗口不可稳定捕获（过渡结束后即被 Ready 帧替换），未纳入断言——以终态
设备名+播放连续性收口；瞬态契约由真机标定后补（template_needs 未涉）。

步骤 → AW 映射：
- 步骤1 本机播放曲目 A 后发起输出切换 → preset_playing("speaker") +
  open_player_page() + read_player_title()（记录 A）+
  select_device(rig_device_name(), via="player")（切换指令派发，会话经
  Switching 过渡至 MediaConfirmed）
- 步骤3 过渡结束断言（T11+P11 契约）→ select_device 内部页头设备名=rig
  断言（设备名=TESTDEV01 语义）+ assert_playing()（播放连续）+
  read_player_title()（A 曲内容确认后按目标端队列呈现，身份区可读）
- 清理 输出切回本机扬声器并停止播放 → close_full_player() → go_home() →
  open_device_page() + select_device("扬声器", via="card") + open_player_page()
  + player_control("pause")
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestCrossDeviceSwitchTransition(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """跨设备切换 Switching 过渡禁显前歌（POS-023）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cross_device_switch_transition(self):
        """本机播 A → 切 rig 音箱 → 过渡结束设备名更新且播放连续。"""
        # 步骤1：本机播放曲目 A，发起输出切换至 rig 音箱
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        title_a = self.userA.read_player_title()
        assert title_a, "起播后读不到曲目 A（Ready 相位未确立）"
        self.userA.select_device(self.userA.rig_device_name(), via="player")
        # 步骤3：过渡结束（MediaConfirmed）——设备名=rig（内部断言）+播放连续
        self.userA.assert_playing()
        title_after = self.userA.read_player_title()
        assert title_after, "切换后身份区不可读（Ready 未恢复）"
        # 清理：输出切回本机扬声器并停止播放（计时收尾）
        self.userA.close_full_player()
        self.userA.go_home()
        self.userA.open_device_page()
        self.userA.select_device("扬声器", via="card")
        self.userA.open_player_page()
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（输出已切回本机并停止播放）。"""
        pass
