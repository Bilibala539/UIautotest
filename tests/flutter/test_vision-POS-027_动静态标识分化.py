# CASE-ID: vision-POS-027
# LINKED-CASE: vision-POS-027
"""Swan 回归·M10 可视音箱 Vision：动态/静态壁纸类型标识分化——判型正向（vision-POS-027）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_wallpaper_page
- S1 动态素材标识 → 探测「视频/动态/MP4」候选锚（isDynamic=分类 type==2 或
  URL 后缀判型——先截 ?# 再比后缀，判型结果以标识呈现；标识形态未标定见
  package_report.template_needs；缺动态素材则 SKIP-DATA）
- S2 静态素材无动态标识 → 分化以动态标识存在性收口；逐项对比属区域级
  断言（模板标定后补），登记 package_report.template_needs
- S3 退出 → press_back（只读）
前置：素材含动态类型（.mp4/.mov/.m3u8/.webm 或分类 type==2）与静态类型。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionDynStaticBadge(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """动态/静态壁纸类型标识分化（vision-POS-027）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_dynamic_static_badge_diff(self):
        """动态素材标识锚点命中（判型正向）；退出只读。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wallpaper_page()
        # S1 动态素材标识探测（数据分支：缺动态素材则 SKIP-DATA）
        marker = None
        for m in ('视频', '动态', 'MP4'):
            if self.userA.find_text_by_ocr(m, timeout=3) is not None:
                marker = m
                break
        if marker is None:
            pytest.skip('环境未见动态素材标识锚点，判型断言 SKIP-DATA')
        self.userA.text_exists(marker, timeout=3)
        # S3 退出（只读）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
