# CASE-ID: nav-NEG-008
"""Swan 回归·M03 主框架导航：底部 Tab 极速连切无卡死（nav-NEG-008）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()
- <100ms 间隔极速连切 20 圈 → rapid_tab_cycle(20)（未选中态 Tab 图 [图]
  连点；UI 自动化单次点击≈1s 截图匹配，<100ms 间隔不可达——以连续无
  间隔轮切逼近压测语义，口径登记 template_needs/notes）
- 页内视频停止/接口轮询停止为内部机制不可观测，不在脚本内表达
- 压测后框架仍可正常响应 → go_bottom_tab("平台")/("设备") 收口断言
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavNeg008RapidTabCycle(SwanRP01Mixin, BaseTest):
    """底部 Tab 极速连切无卡死（nav-NEG-008）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_rapid_tab_cycle_no_freeze(self):
        """20 圈连续轮切后框架仍可正常切 Tab（无卡死/黑屏/崩退）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.rapid_tab_cycle(20)
        self.userA.go_bottom_tab("平台")
        self.userA.go_bottom_tab("设备")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
