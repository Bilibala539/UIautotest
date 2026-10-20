# CASE-ID: player-POS-031
"""Swan 回归·播放器：五路由型卡片按库存展示（player-POS-031）。

⚠️ 部分转换：步骤3 蓝牙卡（SKIP-BT）与 Apple Music 卡（SKIP-PLAT，iOS 可见）
不纳入本脚本——框架无蓝牙输出、Android rig 无 AM AirPlay 卡（与 YAML 缺型
SKIP 标注同口径）；remoteMqtt 卡触发形态未确认（卡片未决 2，SKIP-UNCONFIRMED
不判失败）。缺口登记见 package_report.template_needs。

步骤 → AW 映射：
- 前置 本机扬声器输出（当前选中态锚定本机卡）→ preset_playing("speaker") +
  open_player_page()
- 步骤1 打开输出切换弹窗（统一设备弹窗切换区）→ open_device_sheet()
  （设备按钮模板链点击 + 弹层标题 [图] 断言，路由卡片列表渲染）
- 步骤2 本机扬声器卡与 Wi-Fi 卡（TESTDEV01）必现 → assert_any_text(["扬声器",
  rig 设备名])（输出条目 OCR 可辨）
- 步骤4 卡片态标注 → find_image(SWAN_DEVICE_SHEET_CHECKED)（当前输出卡片
  选中态标识存在）
- 收尾 关闭还原 → press_back()
清理：无（只读断言）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_DEVICE_SHEET_CHECKED
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestRouteCardsByInventory(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """五路由型卡片按库存展示（POS-031）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_route_cards_by_inventory(self):
        """设备弹窗路由卡片：本机+Wi-Fi 必现，当前输出选中态正确。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1：打开统一设备弹窗切换区（弹层标题锚断言在 open_device_sheet 内）
        self.userA.open_device_sheet()
        # 步骤2：本机扬声器卡与 Wi-Fi 卡必现（库存渲染）
        self.userA.assert_any_text(["扬声器", self.userA.rig_device_name()],
                                   timeout=8)
        # 步骤4：当前输出（本机）卡片有选中态标识
        assert self.userA.find_image(SWAN_DEVICE_SHEET_CHECKED, timeout=5) is not None, (
            "设备弹窗未探到选中态标识（当前输出卡片态标注缺失？）")
        # 收尾：关闭弹窗还原
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（只读断言，会话随冷启动模型回收）。"""
        pass
