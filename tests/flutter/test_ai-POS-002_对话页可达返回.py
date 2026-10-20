# CASE-ID: ai-POS-002
"""Swan 回归·AI 助手域：AI 对话页可达与返回（ai-POS-002）。

步骤 → AW 映射：
1. 从 AI 首页进入角色对话页 → go_top_tab("AI") + mixin
   open_ai_chat_by_role("小薇")（画廊卡点入，含发送框「发送消息」+
   底部「内容由AI生成」双锚断言）
2. 对话页顶栏信息区 → 顶栏区(0,60,720,170)断言角色名「小薇」
3. 返回 AI 首页 → press_back → 画廊锚回归（无残留弹层/遮罩）

数据说明：「小薇」为基线账号画廊系统角色卡（roleId!=12，非官方知识库
分支，该分支卡位映射未探索，见 report.notes）。

cleanup：无（只读进入；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiChatPageReachBack(SwanRM09Mixin, BaseTest):
    """AI 对话页可达与返回。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_chat_page_reach_and_back(self):
        """进入小薇对话页，顶栏角色名在位，返回后画廊锚回归。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.assert_ai_home_gallery()

        # 进入对话页（open_ai_chat_by_role 内含发送框+AI 声明锚）
        self.userA.open_ai_chat_by_role("小薇")
        assert self.userA.find_ai_topbar_text("小薇", timeout=10) is not None, (
            "对话页顶栏未见角色名「小薇」[OCR·顶栏区]")

        # 返回 AI 首页
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
