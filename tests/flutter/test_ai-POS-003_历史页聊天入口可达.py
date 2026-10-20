# CASE-ID: ai-POS-003
"""Swan 回归·AI 助手域：历史页经聊天页历史入口可达（ai-POS-003）。

步骤 → AW 映射：
1. 对话页点击历史入口 → 前缀真实执行：open_ai_chat_by_role("小薇")
   （对话页可达）→ 入口 ai_chat_history_action 为无文案图标（顶栏图标群
   OCR 无锚，模板未截取）→ 运行时条件 skip
2-4. 历史页渲染/新建入口存在（不点击）/返回 → AI 首页历史入口路径已由
     ai-POS-024 覆盖；本用例专项是聊天页入口，模板补齐后转全自动，
     新建入口存在性断言为 probe_image + 零点击（与 ai-POS-023 联动）

数据说明：pushReplacement 替换不叠栈、queryMessagePre 20s 双超时兜底
为服务端契约面，UI 侧以页面锚回归覆盖。

cleanup：无（只读冒烟；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHistoryViaChatEntry(SwanRM09Mixin, BaseTest):
    """历史页经聊天页历史入口可达（入口图标未截取前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_via_chat_entry(self):
        """对话页前缀可达后，历史/新建图标缺模板即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：对话页可达（历史入口的宿主页）
        self.userA.open_ai_chat_by_role("小薇")
        # 步骤 1：ai_chat_history_action 无文案图标，模板未截取
        pytest.skip(
            "聊天页历史入口为无文案图标（OCR 无锚），且历史页新建会话入口"
            "同为无文案图标（template_needs: ai_chat_history_action + "
            "ai_history_create_new_chat）——补模板后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
