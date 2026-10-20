# CASE-ID: vision-POS-020
# LINKED-CASE: vision-POS-020
"""Swan 回归·M10 可视音箱 Vision：单平台页素材/方案列表与新建入口存在性（vision-POS-020）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 总页进入平台分组 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_advanced_settings + open_vision_platform_page('酷狗')
  （getAdvancedInfo?terraceType= 正向；平台分组卡文案取环境分组，锚「酷狗」）
- S2 素材/方案列表渲染 → assert_any_text（「方案/素材/新建」锚；无数据时空态合理）
- S3 新建入口存在性 → text_exists('新建')，仅存在性断言——零点击
  （新建提交=uploadVisualInfo type="4" 写——禁区 2；上限 6 属执行记录信息不验证）
- S4 返回总页 → press_back（零写）
前置：专用测试账号已登录；至少一个平台有方案数据（无则列表空态断言）。
清理：零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionPlatformPageEntry(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """单平台页素材/方案列表与新建入口存在性（vision-POS-020）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_page_and_create_entry(self):
        """单平台页落地、列表渲染、新建入口可见（零点击）；返回总页零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 进入某平台分组（单平台页落地）
        self.userA.open_vision_platform_page('酷狗')
        # S2 素材/方案列表渲染锚点
        self.userA.assert_any_text(('方案', '素材', '新建'), timeout=10)
        # S3 新建入口存在性（仅存在性——零点击）
        self.userA.text_exists('新建', timeout=10)
        # S4 返回总页（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
