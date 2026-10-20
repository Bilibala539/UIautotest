# CASE-ID: ai-POS-001
"""Swan 回归·AI 助手域：AI Tab 进入角色主页可达（ai-POS-001）。

步骤 → AW 映射：
1. 点击底部导航 AI Tab → go_top_tab("AI")（含顶 Tab 持久化陷阱防护）
2. 等待角色画廊加载 → mixin assert_ai_home_gallery（角色卡名/入口行 OCR 锚）
3. 纵向滚动浏览背景层 → swipe_up / swipe_down；滚动中底部导航壳锚仍在
   （无崩溃），回顶后画廊锚回归（内容随动无撕裂的可观察面）

cleanup：无（只读浏览，零写零状态变更；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHomePageReachable(SwanRM09Mixin, BaseTest):
    """AI Tab 角色主页（AiPage）可达与画廊加载。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_ai_home_reachable(self):
        """AI Tab 落地角色主页，画廊渲染，纵向滚动往返无异常。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.assert_ai_home_gallery()

        # 纵向滚动：底部导航壳锚仍在（未崩溃未白屏），回顶画廊锚回归
        self.userA.swipe_up()
        assert self.userA.text_exists("首页", timeout=5) is not None, (
            "AI 首页纵向滚动后底部导航壳锚「首页」消失（疑似白屏/崩溃）[OCR]")
        self.userA.swipe_down()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
