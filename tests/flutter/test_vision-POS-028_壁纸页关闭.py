# CASE-ID: vision-POS-028
# LINKED-CASE: vision-POS-028
"""Swan 回归·M10 可视音箱 Vision：壁纸页正常关闭——PageClosePort 统一关页正向（vision-POS-028）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_wallpaper_page
  （完成至少一次浏览——落地断言即浏览完成）
- S1 触发关闭 → press_back（系统返回——统一走 PageClosePort.close，
  纯 Flutter 环境 no-op/常规 pop 正向）
- S2 核对返回上级页面 → text_exists('壁纸')（可视音箱 Tab 内容区壁纸入口可见）
- S3 再次进入并关闭（可重复性）→ open_vision_wallpaper_page + press_back + 复核
前置：已绑定 MG100 TESTDEV-MG100-01 在线（壁纸页已可达）。
清理：只读往返零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionWallpaperClose(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """壁纸页正常关闭——PageClosePort 统一关页正向（vision-POS-028）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_wallpaper_page_close_repeatable(self):
        """壁纸页关闭返回顺畅、二次进出同样顺畅（可重复性正向）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wallpaper_page()
        # S1 触发关闭（系统返回——统一走 PageClosePort.close）
        self.userA.press_back()
        # S2 核对返回上级页面（壁纸入口重新可见，无卡死无黑屏）
        self.userA.text_exists('壁纸', timeout=10)
        # S3 再次进入并关闭（可重复性）
        self.userA.open_vision_wallpaper_page()
        self.userA.press_back()
        self.userA.text_exists('壁纸', timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
