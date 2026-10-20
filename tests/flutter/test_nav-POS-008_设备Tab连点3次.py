# CASE-ID: nav-POS-008
"""Swan 回归·M03 主框架导航：设备 Tab 同页连点 3 次仍停留（nav-POS-008）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()；切设备页 → go_bottom_tab("设备")
- 设备 Tab 连点 3 次 → reclick_bottom_tab_label("设备", 3)（导航标签
  [OCR] 定位——选中态无未选中态模板）
- 仍停留设备页 → [图] SWAN_TAB_DEVICE 未选中态模板不可见断言 +
  [图] SWAN_DEVICE_ADD_BTN 设备页锚点存在（同 go_bottom_tab 到位判据）
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_DEVICE_ADD_BTN, SWAN_TAB_DEVICE
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavPos008ReclickStaysDevice(SwanRP01Mixin, BaseTest):
    """设备 Tab 同页连点 3 次仍停留（nav-POS-008）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_reclick_device_tab_stays(self):
        """连点设备 Tab 3 次后仍应停留在设备页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("设备")
        self.userA.reclick_bottom_tab_label("设备", 3)
        assert self.userA.find_image(SWAN_TAB_DEVICE, timeout=2) is None, (
            "设备 Tab 未选中态图可见——页面已离开设备页（连点触发了跳转）")
        self.userA.image_exists(SWAN_DEVICE_ADD_BTN, timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
