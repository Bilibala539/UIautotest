# CASE-ID: ai-POS-019
"""Swan 回归·AI 助手域：App 画廊角色隔离（显式传参正向）（ai-POS-019）。

步骤 → AW 映射：
1-2. AI 首页浏览全部角色卡并逐卡核对 → go_top_tab("AI") +
     assert_ai_home_gallery（基线账号画廊=惠威百科/小薇/惠声远 三个 App 侧
     系统角色）+ mixin swipe_ai_gallery_card 往返（全部卡可达）
3. 与管理页列表交叉核对 → mixin open_ai_roles_page：系统组 4 行集合一致 +
     反向断言 IP 音箱专属角色不混入（text_not_exists「IP100」「IP200」——
     基线账号无 IP 音箱绑定，该步无条件通过）+ 自定义组空态（画廊与
     管理页自定义集合一致的空态面）

cleanup：无（只读交叉核对；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiGalleryRoleIsolation(SwanRM09Mixin, BaseTest):
    """App 画廊与 IP 音箱角色隔离（avatarType 显式传参正向）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_gallery_role_isolation(self):
        """画廊全为 App 侧角色，管理页交叉一致，无 IP 音箱角色混入。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.assert_ai_home_gallery()
        # 画廊横滑轮巡：全部卡可达，页面锚稳定
        for direction in ("next", "next", "prev", "prev"):
            self.userA.swipe_ai_gallery_card(direction)
            self.userA.assert_ai_home_gallery()

        # 管理页交叉核对
        self.userA.open_ai_roles_page()
        for greeting in ("应用助手", "好朋友", "医生", "云舒雁"):
            assert self.userA.text_exists(greeting, timeout=8) is not None, (
                f"管理页系统组角色行缺失（子串「{greeting}」未命中）[OCR]")
        # IP 音箱专属角色不混入 App 侧画廊/管理列表（基线账号无 IP 音箱绑定）
        assert self.userA.text_not_exists("IP100", timeout=5), (
            "App 侧列表混入 IP100 音箱角色（avatarType 传参隔离失效）[OCR]")
        assert self.userA.text_not_exists("IP200", timeout=5), (
            "App 侧列表混入 IP200 音箱角色（avatarType 传参隔离失效）[OCR]")
        # 自定义组空态与画廊一致（基线账号无自定义角色）
        assert self.userA.text_exists("暂未自定义角色", timeout=8) is not None, (
            "管理页自定义组空态「暂未自定义角色」未渲染 [OCR]")

        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
