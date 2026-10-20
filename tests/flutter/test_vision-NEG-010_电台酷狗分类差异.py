# CASE-ID: vision-NEG-010
# LINKED-CASE: vision-NEG-010
"""Swan 回归·M10 可视音箱 Vision：电台判定边界——酷狗（4）非电台、0/5/6 电台（vision-NEG-010）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_advanced_settings
- S1 电台类平台（terraceType 0/5/6 任一）编辑器 → open_vision_scheme_editor('电台')，
  断言分类项中无「歌词」（电台无歌词——_isVisionRadioTerrace）
- S2 酷狗（terraceType=4）编辑器 → open_vision_scheme_editor('酷狗')，
  断言分类项中有「歌词」（酷狗非电台）
- S3 分类多选/单选边界 → 气质/歌词多选、壁纸/氛围单选的选中态分化依赖
  素材选中态标识（未标定），由 vision-POS-021/022 域承载，本用例收口歌词分类差异
前置：高级方案编辑器含酷狗与电台类平台数据（需人工预置/确认）。
清理：不保存退出零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionRadioKugouCategory(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """电台判定边界——酷狗（4）非电台、0/5/6 电台（vision-NEG-010）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_radio_kugou_lyrics_category_diff(self):
        """电台类编辑器无歌词分类、酷狗编辑器有歌词分类；不保存退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 电台类平台编辑器：分类项中无歌词（电台正向）
        self.userA.open_vision_scheme_editor('电台')
        self.userA.text_not_exists('歌词', timeout=8)
        self.userA.press_back()
        self.userA.press_back()
        # S2 酷狗编辑器：有歌词分类（酷狗非电台）
        self.userA.open_vision_scheme_editor('酷狗')
        self.userA.text_exists('歌词', timeout=10)
        # S3 不保存直接返回（零写残留）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
