# CASE-ID: vision-NEG-004
# LINKED-CASE: vision-NEG-004
"""Swan 回归·M10 可视音箱 Vision：编辑器切平台清空全部分类已选（vision-NEG-004）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_advanced_settings
- S1 勾选跨分类素材 → open_vision_scheme_editor('酷狗') + pick_vision_editor_materials
  （音律 2 项+歌词 1 项；条目文案候选未标定，勾选数不足判 SKIP-DATA——见
  package_report.template_needs）
- S2 切换到另一平台 → press_back 出编辑器 → open_vision_platform_page('电台')
  → 重进编辑器（退化口径：经总页换平台；编辑器内平台切换控件未标定）
  → 已选清空 = 选中态候选标识 text_not_exists（负向弱断言，标定后换强断言）
- S3 返回不保存（零写）+ S4 重进复核已选为空 → 重复 S2 负向断言
前置：编辑器音律+歌词分类可用；电台类平台分组卡存在（缺型 SKIP-DATA 归环境）。
清理：全程不保存（选择态零写）；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin

# 已选/选中态标识候选（文案未标定，语义预测——标定后补强断言）
_SELECTED_HINTS = ('已选', '已勾选', '使用中', '正在使用')


class TestSchemeSwitchClearsPicks(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """编辑器切平台清空全部分类已选（vision-NEG-004）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_switch_platform_clears_all_picks(self):
        """勾选跨分类素材→切平台→已选全清；重进复核为空（零保存）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 音律勾 2 + 歌词勾 1（条目锚未标定→勾选数不足判 SKIP-DATA）
        self.userA.open_vision_scheme_editor('酷狗')
        picked = (self.userA.pick_vision_editor_materials('音律', 2)
                  + self.userA.pick_vision_editor_materials('歌词', 1))
        if picked < 3:
            pytest.skip(f'编辑器素材条目锚未标定({picked}/3),分桶断言 SKIP-DATA')
        self.userA.press_back()
        # S2 切换到另一平台（经总页换平台）→ 已选清空（负向弱断言）
        self.userA.open_vision_platform_page('电台')
        self.userA.open_vision_scheme_editor('电台')
        for hint in _SELECTED_HINTS:
            self.userA.text_not_exists(hint, timeout=3)
        # S3+S4 返回不保存，重进复核已选为空（与步骤 2 一致）
        self.userA.press_back()
        self.userA.press_back()
        self.userA.open_vision_platform_page('酷狗')
        self.userA.open_vision_scheme_editor('酷狗')
        for hint in _SELECTED_HINTS:
            self.userA.text_not_exists(hint, timeout=3)
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
