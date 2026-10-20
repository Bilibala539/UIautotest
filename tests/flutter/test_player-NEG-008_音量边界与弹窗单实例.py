# CASE-ID: player-NEG-008
"""Swan 回归·播放器：音量边界 0/100 与弹窗单实例（播放页入口）（player-NEG-008）。

⚠️ 部分转换：步骤4-7（弹窗关闭 TBD·语义三入口轮开 / FM 底部栏入口 /
设备卡片入口 / 物理音量键目标断言）依赖未截取元素与物理按键，未纳入本
脚本——缺口登记见 package_report.template_needs；本脚本覆盖步骤1-3
播放页入口链路。

步骤 → AW 映射：
- 前置 Wi-Fi 音箱输出 → preset_playing("wifi_device")（volume_child_slider
  目标可达）
- 步骤1 播放页打开音量弹窗（单实例出现）→ open_volume_popup()（图标模板链
  点击 + 弹层锚 [图] 断言）
- 步骤2 主滑杆拖到 0（下界不越界，mute 联动）→ set_volume(0)（±锚定拖拽 +
  弹层内百分比断言，坑 8 口径：UI 展示值仅作 UI 层断言）
- 步骤3 主滑杆拖到 100（上界不越界，无溢出崩溃）→ set_volume(100)
- 收尾 写副作用还原 → set_volume(50)（坑 9 注记：遗留设备音量会污染后续用例）
清理：音量还原 50；teardown pass。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestVolumeBoundaryPopupSingleInstance(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """音量边界与弹窗单实例（播放页入口）（NEG-008）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_volume_boundary_popup_single_instance(self):
        """播放页音量弹窗：单实例出现 + 0/100 边界不越界 + 写副作用还原。"""
        self.userA.preset_playing("wifi_device")
        self.userA.open_player_page()
        # 步骤1：弹窗单实例出现（弹层锚断言在 open_volume_popup 内）
        self.userA.open_volume_popup()
        self.userA.press_back()
        # 步骤2：拖到 0——下界不越界、mute 联动（百分比断言在 set_volume 内）
        self.userA.set_volume(0)
        # 步骤3：拖到 100——上界不越界、无溢出
        self.userA.set_volume(100)
        # 收尾：写副作用还原（遗留设备音量会污染后续用例）
        self.userA.set_volume(50)

    def teardown(self) -> None:
        """无用例私有清理（音量已还原 50，会话随冷启动模型回收）。"""
        pass
