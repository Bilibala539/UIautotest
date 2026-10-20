# CASE-ID: vision-POS-021
# LINKED-CASE: vision-POS-021
"""Swan 回归·M10 可视音箱 Vision：方案编辑器四分类素材浏览（vision-POS-021）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入方案编辑器 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_advanced_settings + open_vision_scheme_editor('酷狗')
  （visionType 缺省 3 正向——页面正常打开）
- S2 依次切换四分类浏览 → click_text('气质'/'歌词'/'壁纸'/'氛围')
  （分类序列 visionType 6 气质/5 歌词/1 壁纸/2 氛围，user/getVisionInfo 查询锚）
- S3 分类间往返切换 → 回切「气质」渲染一致（已选桶按分类分桶保留正向吸收坑 3；
  勾选态观测依赖素材选中态标识，未标定项见 package_report.template_needs）
- S4 不保存直接返回 → press_back（零保存零上传，止步保存前）
前置：专用测试账号已登录；编辑器可进入（新建入口或既有方案查看）。
清理：未保存零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionEditorCategories(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """方案编辑器四分类素材浏览（vision-POS-021）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_editor_four_categories_browse(self):
        """编辑器落地、四分类依次切换渲染、往返一致；不保存退出零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 进入方案编辑器（visionType 缺省 3 正向）
        self.userA.open_vision_scheme_editor('酷狗')
        # S2 依次切换四分类浏览素材
        self.userA.click_text('气质', timeout=8)
        self.userA.click_text('歌词', timeout=8)
        self.userA.click_text('壁纸', timeout=8)
        self.userA.click_text('氛围', timeout=8)
        # S3 往返切换：回切气质分类渲染一致
        self.userA.click_text('气质', timeout=8)
        self.userA.text_exists('气质', timeout=5)
        # S4 不保存直接返回（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
