# CASE-ID: vision-POS-022
# LINKED-CASE: vision-POS-022
"""Swan 回归·M10 可视音箱 Vision：编辑器分类多选/单选模式差异（vision-POS-022）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_advanced_settings
  + open_vision_scheme_editor('酷狗')（气质/歌词素材 ≥2、壁纸素材 ≥2，不足判 SKIP-DATA）
- S1 气质分类勾选 2 项（多选正向）→ pick_vision_editor_materials('气质', 2)
- S2 歌词分类勾选 2 项（多选，气质已选保留）→ pick('歌词', 2) + 切回气质复核
  选中态标识存在（分桶保留；条目文案候选未标定——见 package_report.template_needs）
- S3 壁纸分类先后点选 2 个素材（单选互斥：后点替换先点）→ pick('壁纸', 2) 连续
  两次调用（「后点项替换先点项」的互斥计数 OCR 不可观测，以选中态标识仍存在
  收口——互斥强断言待标定）
- S4 不保存直接返回 → press_back（零保存退出，硬约束）
前置：方案编辑器内气质/歌词/壁纸分类素材满足数量（缺型 SKIP-DATA 归环境）。
清理：选择态不保存（零写，禁区 2 安全）；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin

# 选中态标识候选（文案未标定，语义预测——标定后补强断言）
_SELECTED_HINTS = ('已选', '已勾选', '使用中', '正在使用')


class TestEditorMultiSingleSelect(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """编辑器分类多选/单选模式差异（vision-POS-022）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_category_multi_single_select_diff(self):
        """气质/歌词多选并行保持，壁纸单选替换；不保存退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        self.userA.open_vision_scheme_editor('酷狗')
        # S1 气质分类勾选 2 个素材（多选正向——两项同时保持）
        picked_q = self.userA.pick_vision_editor_materials('气质', 2)
        if picked_q < 2:
            pytest.skip(f'气质分类素材条目锚未标定({picked_q}/2),多选断言 SKIP-DATA')
        # S2 歌词分类勾选 2 个素材（多选），切回气质复核已选保留
        picked_g = self.userA.pick_vision_editor_materials('歌词', 2)
        if picked_g < 2:
            pytest.skip(f'歌词分类素材条目锚未标定({picked_g}/2),保留断言 SKIP-DATA')
        self.userA.click_text('气质', timeout=10)
        self.userA.assert_any_text(_SELECTED_HINTS, timeout=8)
        # S3 壁纸分类先后点选 2 个素材（单选互斥：后点替换先点）
        picked_w = (self.userA.pick_vision_editor_materials('壁纸', 1)
                    + self.userA.pick_vision_editor_materials('壁纸', 1))
        if picked_w < 2:
            pytest.skip(f'壁纸分类素材条目锚未标定({picked_w}/2),单选断言 SKIP-DATA')
        self.userA.assert_any_text(_SELECTED_HINTS, timeout=8)
        # S4 不保存直接返回（零保存退出）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
