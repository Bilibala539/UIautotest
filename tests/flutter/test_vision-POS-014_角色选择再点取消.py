# CASE-ID: vision-POS-014
# LINKED-CASE: vision-POS-014
"""Swan 回归·M10 可视音箱 Vision：AI 角色选择态与再点取消（vision-POS-014）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_ai_roles_page
- S1 初始无选中高亮 → text_not_exists（「已选择/使用中」选中态标识候选）
- S2 点选角色 A → click_text('小薇')（系统角色名锚，知识库 swan_所有角色页），
  断言选中态标识出现
- S3 再点角色 A → 取消选中（再点当前角色=取消），断言标识消失
- S4 点选角色 B → click_text('惠威百科')，断言标识出现后直接 press_back
  （不点保存——uploadVisualInfo type="2" 整表上传零触发，止步保存前）
前置：系统角色 ≥2（小薇/惠威百科，知识库实测角色集）；已绑定 MG100。
清理：未保存零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionRoleSelectToggle(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """Vision AI 角色选择态与再点取消（vision-POS-014）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_role_select_and_toggle_off(self):
        """无选中 → 点 A 选中 → 再点取消 → 点 B 选中 → 返回零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_ai_roles_page()
        # S1 初始无选中高亮（selectedRoleId=-1 正向）
        self.userA.text_not_exists('已选择', timeout=3)
        self.userA.text_not_exists('使用中', timeout=3)
        # S2 点选角色 A：选中态标识出现
        self.userA.click_text('小薇', timeout=10)
        marker = self.userA.assert_any_text(('已选择', '使用中'), timeout=10)
        # S3 再点角色 A：取消选中（标识消失）
        self.userA.click_text('小薇', timeout=10)
        self.userA.text_not_exists(marker, timeout=5)
        # S4 点选角色 B 后直接返回（零上传零同步，重进还原）
        self.userA.click_text('惠威百科', timeout=10)
        self.userA.assert_any_text(('已选择', '使用中'), timeout=10)
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
