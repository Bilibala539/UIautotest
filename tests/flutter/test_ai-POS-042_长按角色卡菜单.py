# CASE-ID: ai-POS-042
"""Swan 回归·AI 助手域：长按角色卡遮罩操作菜单唤起与关闭（ai-POS-042）。

步骤 → AW 映射：
1. 长按任一角色卡 → go_top_tab("AI") + assert_ai_home_gallery +
   long_press_text("小薇")（画廊卡名长按）
2. 浏览菜单项 → 断言遮罩菜单出现（YAML expect 菜单项「编辑/删除」按实际
   形态——若菜单为图标形态需执行轮标定，见 report.template_needs；
   ⛔ 删除类操作仅存在性断言，零点击零确认）
3. 关闭菜单 → 遮罩空白处无坐标点击能力（框架禁硬编码坐标），以返回键
   等价关闭（形态执行轮记录），断言画廊锚回归（无残留遮罩）

cleanup：无（零删除零状态变更；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiCardLongPressMaskMenu(SwanRM09Mixin, BaseTest):
    """长按角色卡遮罩操作菜单唤起与关闭（删除零触发）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_card_longpress_mask_menu(self):
        """长按出遮罩菜单（编辑/删除项），返回键关闭后画廊无残留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.assert_ai_home_gallery()

        # 长按角色卡 → 遮罩操作菜单
        self.userA.long_press_text("小薇", timeout=10)
        assert self.userA.assert_any_text(("编辑", "删除"), timeout=8), (
            "长按角色卡后遮罩操作菜单未出现（菜单项「编辑/删除」均未命中，"
            "若为图标形态需标定）[OCR]")

        # 关闭菜单（⛔ 删除项零点击）：返回键等价关闭遮罩
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
