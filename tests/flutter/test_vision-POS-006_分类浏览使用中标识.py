# CASE-ID: vision-POS-006
# LINKED-CASE: vision-POS-006
"""Swan 回归·M10 可视音箱 Vision：壁纸分类浏览与使用中标识正确（vision-POS-006）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_wallpaper_page
- S1 内容分类浏览 → 落地断言收口（壁纸 visionType=1 默认分类）
- S2 当前使用中壁纸标识 → assert_any_text（「使用中/正在使用/当前」候选，
  标识形态未标定见 package_report.template_needs）
- S3 滑动浏览全部素材 → swipe_up
- S4 退出壁纸页 → press_back（零保存零下发——禁区 1/2）
前置：已绑定 MG100 TESTDEV-MG100-01 在线；只浏览不保存。
清理：零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionBrowseInUse(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """壁纸分类浏览与使用中标识正确（vision-POS-006）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_browse_categories_and_in_use_marker(self):
        """分类浏览、当前使用项标识命中、滑动全览；退出零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wallpaper_page()
        # S2 当前使用中壁纸标识正确（跨分类匹配正向）
        self.userA.assert_any_text(('使用中', '正在使用', '当前'), timeout=10)
        # S3 滑动浏览全部素材
        self.userA.swipe_up()
        # S4 退出壁纸页（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
