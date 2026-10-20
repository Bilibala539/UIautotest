# CASE-ID: vision-POS-002
# LINKED-CASE: vision-POS-002
"""Swan 回归·M10 可视音箱 Vision：壁纸页素材网格加载与分类可达（vision-POS-002）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_wallpaper_page
- S1 素材加载渲染 → 落地断言收口（open_vision_wallpaper_page 落地锚）
- S2 分类切换浏览 → click_text('氛围')（visionType=2）→ click_text('壁纸')（visionType=1）
- S3 缩略图加载 → 分类切换后页面稳定渲染（216x124 规格断言归模板标定，
  见 package_report.template_needs）
- S4 返回退出 → press_back
前置：已绑定 MG100 TESTDEV-MG100-01 在线（Vision 入口依赖）。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionGridAndCategories(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """壁纸页素材网格加载与分类可达（vision-POS-002）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_wallpaper_grid_and_categories(self):
        """壁纸主页落地 → 氛围/壁纸分类往返切换渲染 → 返回退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wallpaper_page()
        # S2 切换氛围分类（visionType=2）浏览
        self.userA.click_text('氛围', timeout=10)
        self.userA.text_exists('氛围', timeout=5)
        # S3 切回壁纸分类（visionType=1）
        self.userA.click_text('壁纸', timeout=10)
        self.userA.text_exists('壁纸', timeout=5)
        # S4 返回退出（关页统一走 PageClosePort）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
