# CASE-ID: ai-POS-043
"""Swan 回归·AI 助手域：角色画廊 PageView 横滑浏览（ai-POS-043）。

步骤 → AW 映射：
1-3. 画廊横滑翻页/回滑/连续轮巡 → go_top_tab("AI") +
     mixin swipe_ai_gallery_card（next=下一张，prev=回滑；窗口动态坐标
     规避硬编码）：next→prev 往返 + next×2 轮巡，每步画廊锚与历史入口行
     回归（全部卡可达无白屏无崩溃的可观察面）。3D transform 流畅度与
     遮罩补偿为视觉判定域（OCR 不可及），形态执行轮记录，
     见 report.template_needs。

数据说明：基线账号画廊 3 张系统角色卡（惠威百科/小薇/惠声远），满足
≥2 卡前置；横滑对 PageView 的翻页效果经锚稳定性间接核实。

cleanup：无（只读浏览；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiGalleryPageViewSwipe(SwanRM09Mixin, BaseTest):
    """角色画廊 PageView 横滑浏览。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_gallery_pageswipe_roundtrip(self):
        """横滑往返 + 连续轮巡，画廊锚与历史入口行全程稳定。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.assert_ai_home_gallery()

        # 往返：下一张 → 回滑原卡
        self.userA.swipe_ai_gallery_card("next")
        self.userA.assert_ai_home_gallery()
        self.userA.swipe_ai_gallery_card("prev")
        self.userA.assert_ai_home_gallery()

        # 连续轮巡：下一张×2 → 回滑×2
        self.userA.swipe_ai_gallery_card("next")
        self.userA.swipe_ai_gallery_card("next")
        self.userA.assert_ai_home_gallery()
        self.userA.swipe_ai_gallery_card("prev")
        self.userA.swipe_ai_gallery_card("prev")
        self.userA.assert_ai_home_gallery()

        # 页面完整性：历史入口行仍在（无白屏无残留遮罩）
        assert self.userA.text_exists("历史对话记录", timeout=8) is not None, (
            "横滑轮巡后 AI 首页历史入口行缺失（页面完整性异常）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
