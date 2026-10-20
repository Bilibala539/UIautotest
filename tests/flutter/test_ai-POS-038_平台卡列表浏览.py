# CASE-ID: ai-POS-038
"""Swan 回归·AI 助手域：平台管理页平台卡列表展示态与滚动（ai-POS-038）。

步骤 → AW 映射：
1. 进入 AI 平台管理页 → go_top_tab("AI") + mixin open_ai_role_editor() +
   click_text("更多AI平台")（入口位于编辑器内，wave5 实测路径）
2-3. 平台卡逐项渲染与逐卡滚动浏览 → 首屏断言 Qwen/DeepSeek/豆包/Kimi，
     swipe_up 滚动后断言尾部「腾讯混元」，swipe_down 回顶断言「Qwen」
     （列表滚动随动的可观察面，无白屏无崩溃；⛔ 全程不点平台行按钮——
     点击弹授权门禁）

cleanup：无（展示态用例；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiPlatformListBrowse(SwanRM09Mixin, BaseTest):
    """平台管理页平台卡列表展示态与滚动浏览。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_list_browse(self):
        """平台卡首屏/滚动后渲染完整，往返滚动无白屏。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()
        self.userA.click_text("更多AI平台", timeout=10)

        # 首屏平台卡（wave5 实测单屏 8 行，取头部 4 行断言）
        for platform in ("Qwen", "DeepSeek", "豆包", "Kimi"):
            assert self.userA.text_exists(platform, timeout=8) is not None, (
                f"平台管理页平台卡「{platform}」未渲染 [OCR]")
        # 滚动到尾部再回顶（⛔ 不点行按钮）
        self.userA.swipe_up()
        assert self.userA.text_exists("腾讯混元", timeout=8) is not None, (
            "平台列表滚动后尾部平台卡「腾讯混元」未渲染 [OCR]")
        self.userA.swipe_down()
        assert self.userA.text_exists("Qwen", timeout=8) is not None, (
            "平台列表回顶后头部平台卡「Qwen」未渲染 [OCR]")

        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "平台管理页返回后未回到角色编辑器 [OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
