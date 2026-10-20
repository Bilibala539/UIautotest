# CASE-ID: player-POS-010
"""Swan 回归·播放器：底栏迷你播放器长按展开（player-POS-010）。

⚠️ B 标定项（ADD1 改判）：expanded 大卡形态未探索、收起操作 TBD·语义——
长按手势框架已具备（long_press_image，模板锚定非坐标），按 OCR 优先转换：
mini→长按展开→形态变化断言走通；expanded 卡锚与收起操作留 template_needs
待标定。

步骤 → AW 映射：
- 前置 起播回首页（mini 形态：曲名+控件紧凑布局）→ preset_playing("speaker")
  + close_full_player() + go_home()
- 步骤1 mini 形态在位 → assert_bottom_bar_session(True)（band 设备名签名行）
  + OCR 记录 band 基线
- 步骤2 长按底栏迷你播放器 → long_press_image(SWAN_BOTTOM_PLAYER_BAR,
  duration=1.5)（模板锚定长按）→ OCR 断言 band 形态变化（expanded 大卡
  出现致 band 区域文本改变）
- 步骤3 expanded 收起（TBD·语义）→ press_back() 代理 + mini 形态回归断言
  （assert_bottom_bar_session(True)）；播放不中断由 player 页复核
清理：停止播放 → open_player_page() + player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_BOTTOM_PLAYER_BAR
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestMiniBarLongPressExpand(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """底栏迷你播放器长按展开（POS-010，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_mini_bar_long_press_expand(self):
        """mini 在位 → 长按展开（形态变化）→ 收起回归 mini 且播放连续。"""
        self.userA.preset_playing("speaker")
        self.userA.close_full_player()
        self.userA.go_home()
        # 步骤1：mini 形态在位，记录 band 基线
        self.userA.assert_bottom_bar_session(True)
        before = [i["text"] for i in
                  self.userA.ocr_scan_page(region=(0, 1290, 720, 196))]
        # 步骤2：长按底栏迷你播放器（模板锚定），断言展开形态出现
        self.userA.long_press_image(SWAN_BOTTOM_PLAYER_BAR, timeout=5, duration=1.5)
        after = [i["text"] for i in
                 self.userA.ocr_scan_page(region=(0, 1290, 720, 196))]
        assert after != before, (
            f"长按后 band 区域 OCR 无变化（expanded 态未出现？）before={before} "
            f"after={after}")
        # 步骤3：收起（TBD·语义，back 代理）→ mini 形态回归
        self.userA.press_back()
        self.userA.assert_bottom_bar_session(True)
        # 播放不中断复核
        self.userA.open_player_page()
        self.userA.assert_playing()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
