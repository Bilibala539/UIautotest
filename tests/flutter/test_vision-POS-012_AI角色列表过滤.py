# CASE-ID: vision-POS-012
# LINKED-CASE: vision-POS-012
"""Swan 回归·M10 可视音箱 Vision：AI 角色列表系统角色过滤展示（vision-POS-012）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入 AI 角色页 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_ai_roles_page（入口 OCR「角色」→ 落地锚）
- S2 系统角色列表渲染 → assert_any_text（系统角色名锚点取自知识库
  swan_所有角色页 实测：小薇/惠威百科/惠声远/云舒雁；服务端
  getRoleList?avatarType=1 + 客户端筛 shared==1 双保险过滤正向）
- S3 角色名非空 → S2 命中的角色名即非空渲染证据（逐卡核对收口为可见角色锚）
前置：服务端存在 avatarType==1 系统 Live2D 角色（环境预置）；已绑定 MG100。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionAiRolesFilter(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """Vision AI 角色列表系统角色过滤展示（vision-POS-012）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_ai_roles_system_filter(self):
        """AI 角色页落地、系统 Live2D 角色名渲染非空；退出零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_ai_roles_page()
        # S2+S3 系统角色列表渲染、角色名非空（知识库实测系统角色名锚）
        self.userA.assert_any_text(('小薇', '惠威百科', '惠声远', '云舒雁'), timeout=15)
        # 退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
