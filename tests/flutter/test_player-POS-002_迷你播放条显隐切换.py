# CASE-ID: player-POS-002
"""Swan 回归·播放器：底栏迷你播放条显隐切换（player-POS-002）。

步骤 → AW 映射：
- 步骤1 起播后返回首页（非全屏页）→ preset_playing("speaker") → close_full_player()
  （收起钮模板链）→ go_home()（首页锚）→ assert_bottom_bar_session(True)
  （band 内「扬声器」签名行=播放会话条带常驻）
- 步骤2 点击底栏迷你播放器进全屏页 → click_bottom_player_bar() + open_player_page()
  → assert_bottom_bar_session(False)（全屏页内条带按契约隐藏，band 仅剩页面自身文本）
- 步骤3 点击关闭按钮退出全屏页 → close_full_player()（player_dismiss_button
  模板链，非盲 back）→ assert_bottom_bar_session(True)（条带恢复可见）

bottomBar 独立路由常驻回归面：全屏页外常驻可见、全屏页内隐藏、进出显隐切换正确。
清理：显式停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestBottomBarVisibilityToggle(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """底栏迷你播放条显隐切换（POS-002）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_bottom_bar_visibility_toggle(self):
        """起播回首页条带可见 → 进全屏页隐藏 → 退出恢复可见。"""
        self.userA.preset_playing("speaker")
        # 步骤1：收全屏页回首页，底栏迷你播放条可见（非全屏页常驻）
        self.userA.close_full_player()
        self.userA.go_home()
        self.userA.assert_bottom_bar_session(True)
        # 步骤2：点底栏迷你播放器进全屏页，条带按契约隐藏
        self.userA.click_bottom_player_bar()
        self.userA.open_player_page()
        self.userA.assert_bottom_bar_session(False)
        # 步骤3：点关闭钮退出全屏页，条带恢复可见
        self.userA.close_full_player()
        self.userA.assert_bottom_bar_session(True)
        # 清理：显式停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
