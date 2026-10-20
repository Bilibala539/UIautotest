# CASE-ID: player-POS-030
"""Swan 回归·播放器：统一设备弹窗三区可达（player-POS-030）。

⚠️ 部分转换：步骤2 同步设备条目五字段语义（isSourceDevice/isExistingSlave/
isCompatible/incompatibility/isAppleMusicAirPlay）依赖可同步设备数据态与
字段级 UI 呈现，未逐字段断言——以弹层内输出设备行 OCR 可辨收口；
AM AirPlay 区卡片依赖未截取模板（登记 template_needs）。

步骤 → AW 映射：
- 前置 播放页可达 → preset_playing("speaker") + open_player_page()
- 步骤1 点击设备入口打开统一设备弹窗 → open_device_sheet()（设备按钮模板链
  点击 + 弹层标题 [图] 断言）
- 三区可达断言 → assert_any_text(["扬声器", rig 设备名])（输出设备条目 OCR 可辨）
- 步骤3 关闭弹窗还原 → press_back() → find_image(SWAN_PLAYER_PROGRESS_BAR)
  （回播放页无残留）
清理：无（只读断言；teardown pass）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYER_PROGRESS_BAR
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestDeviceSheetThreeSections(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """统一设备弹窗三区可达（POS-030）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_device_sheet_three_sections(self):
        """播放页设备入口开弹窗 → 条目可辨 → 关闭还原回播放页。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1：打开统一设备弹窗（弹层标题锚断言在 open_device_sheet 内）
        self.userA.open_device_sheet()
        # 三区可达：输出设备条目 OCR 可辨（本机/rig 至少其一在弹层内）
        self.userA.assert_any_text(["扬声器", self.userA.rig_device_name()],
                                   timeout=8)
        # 步骤3：关闭弹窗还原，回播放页无残留
        self.userA.press_back()
        assert self.userA.find_image(SWAN_PLAYER_PROGRESS_BAR, timeout=5) is not None, (
            "关闭设备弹窗后未回到播放页（进度条锚未命中）")

    def teardown(self) -> None:
        """无用例私有清理（只读断言，会话随冷启动模型回收）。"""
        pass
