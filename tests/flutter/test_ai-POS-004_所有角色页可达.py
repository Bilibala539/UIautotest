# CASE-ID: ai-POS-004
"""Swan 回归·AI 助手域：角色管理页（所有角色）可达（ai-POS-004）。

步骤 → AW 映射：
1. AI 首页点角色管理入口 → mixin open_ai_roles_page（经
   SWAN_HOME_AI_ROLE_SETTINGS [图] 入口，到位断言顶栏页题「所有角色」）
2. 角色行列表渲染 → 断言系统组 4 行（应用助手/好朋友/医生/云舒雁子串，
   规避 OCR 全半角逗号抖动）+ 底部「添加更多AI角色」入口
3. 二级页通用返回 → press_back 回 AI 首页，画廊锚回归（无栈残留）

cleanup：无（只读浏览；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRolesManagePageReachable(SwanRM09Mixin, BaseTest):
    """角色管理页（/ai/role/manage）可达与列表渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_roles_manage_page_reachable(self):
        """所有角色页落地，系统组角色行渲染，返回无栈残留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_roles_page()

        # 系统组角色行（问候语子串，OCR 逗号全/半角抖动免疫）
        for greeting in ("应用助手", "好朋友", "医生", "云舒雁"):
            assert self.userA.text_exists(greeting, timeout=8) is not None, (
                f"所有角色页系统组角色行缺失（问候语子串「{greeting}」未命中）[OCR]")
        # 底部新建入口行
        assert self.userA.text_exists("添加更多AI角色", timeout=8) is not None, (
            "所有角色页底部「添加更多AI角色」入口缺失 [OCR]")

        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
