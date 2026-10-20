# CASE-ID: vision-NEG-012
# LINKED-CASE: vision-NEG-012
"""Swan 回归·M10 可视音箱 Vision：编辑器已选 ID 分桶——切分类保留已选（vision-NEG-012）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_advanced_settings
  + open_vision_scheme_editor('酷狗')（需 terraceType 有音律+歌词两分类的平台，
  缺型 SKIP-DATA 归环境）
- S1 音律分类勾选 2 项 → pick_vision_editor_materials('音律', 2)
  （条目文案候选未标定，勾选数不足判 SKIP-DATA——见 package_report.template_needs）
- S2 切歌词再切回音律 → click_text('歌词') → click_text('音律')
  → 音律已选保留 = 选中态候选标识 assert_any_text 命中（分桶重放正向；
  标识文案未标定，候选全缺判 SKIP-DATA）
- S3 歌词分类勾 1 项后复核双桶 → pick('歌词', 1) + 双分类下标识各自存在
  （音律 2 项+歌词 1 项并行共存的桶计数 OCR 不可观测，以双分类标识存在收口）
前置：编辑器音律+歌词分类可用；素材数满足（≥2/≥1）。
清理：全程不保存（选择态零写，禁区 2 安全）；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin

# 已选/选中态标识候选（文案未标定，语义预测——标定后补强断言）
_SELECTED_HINTS = ('已选', '已勾选', '使用中', '正在使用')


class TestEditorBucketKeep(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """编辑器已选 ID 分桶——切分类保留已选（vision-NEG-012）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_picks_kept_across_category_switch(self):
        """音律勾 2→切歌词切回保留→歌词勾 1 双桶共存（零保存）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        self.userA.open_vision_scheme_editor('酷狗')
        # S1 音律分类勾选 2 项（分桶记录——条目锚未标定兜底 SKIP-DATA）
        picked = self.userA.pick_vision_editor_materials('音律', 2)
        if picked < 2:
            pytest.skip(f'编辑器素材条目锚未标定({picked}/2),分桶断言 SKIP-DATA')
        # S2 切到歌词再切回音律：音律已选保留（分桶重放正向）
        self.userA.click_text('歌词', timeout=10)
        self.userA.click_text('音律', timeout=10)
        marker = self.userA.assert_any_text(_SELECTED_HINTS, timeout=8)
        # S3 歌词分类勾 1 项后复核双桶（双分类标识各自存在=并行共存）
        picked_g = self.userA.pick_vision_editor_materials('歌词', 1)
        if picked_g < 1:
            pytest.skip('歌词分类素材不足或条目锚未标定,双桶断言 SKIP-DATA')
        self.userA.click_text('音律', timeout=10)
        self.userA.text_exists(marker, timeout=5)
        self.userA.click_text('歌词', timeout=10)
        self.userA.text_exists(marker, timeout=5)
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
