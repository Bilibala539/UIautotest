# CASE-ID: ai-POS-005
"""Swan 回归·AI 助手域：AI 平台管理页可达与平台卡渲染（ai-POS-005）。

步骤 → AW 映射：
1. 进入 AI 平台管理页 → go_top_tab("AI") + mixin open_ai_role_editor() +
   click_text("更多AI平台")（入口位于角色编辑器内，wave5 实测路径）
2. 页面可达性 → 顶栏区页题「平台」+ 弹层标题图锚
   probe_image(SWAN_AI_PLATFORM_TITLE)（页题文本 OCR 与图像模板双锚）
3. 平台卡渲染 → 断言 Qwen/DeepSeek/豆包/Kimi（wave5 实测单屏 8 行，取
   头部 4 行代表断言；⛔ 全程不点平台行按钮——点击弹授权门禁/添加拦截）
4. 返回 → press_back 回编辑器锚 → 再 press_back 回画廊锚

数据说明：授权平台数为 0（基线账号），用例只验证平台管理页可达与列表
渲染，不涉及授权态平台卡（该分支见 ai-POS-039 跳过记录）。

cleanup：无（展示态用例；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_AI_PLATFORM_TITLE
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiPlatformPageReach(SwanRM09Mixin, BaseTest):
    """AI 平台管理页可达与平台卡渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_page_reach_and_render(self):
        """平台管理页可达，页题双锚在位，平台卡渲染完整。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 进入平台管理页
        self.userA.click_text("更多AI平台", timeout=10)
        assert self.userA.find_ai_topbar_text("平台", timeout=10) is not None, (
            "平台管理页顶栏未见页题「平台」[OCR·顶栏区]")
        assert self.userA.probe_image(SWAN_AI_PLATFORM_TITLE, timeout=8) is not None, (
            "平台管理页标题行 [图] 未命中（页面未达或模板需标定）")

        # 平台卡渲染（⛔ 不点行按钮）
        for platform in ("Qwen", "DeepSeek", "豆包", "Kimi"):
            assert self.userA.text_exists(platform, timeout=8) is not None, (
                f"平台管理页平台卡「{platform}」未渲染 [OCR]")

        # 返回：编辑器 → AI 首页
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "平台管理页返回后未回到角色编辑器 [OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
