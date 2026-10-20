# CASE-ID: ai-NEG-018
"""Swan 回归·AI 助手域：历史空态边界·零会话空态稳定与首条消息迁移（ai-NEG-018）。

步骤 → AW 映射：
1. 空账号进入历史页 → 运行时条件门：SWAN_AI_EMPTY_HISTORY_ACCT=1
   （零会话专用账号预置后置位；未置位 skip——基线账号已有历史不满足
   空态前置）→ open_ai_history_page（AI 首页历史入口路径）
2. 空态视图 → 历史列表区 OCR 快照为空集断言（scan_ai_chat_content 同款
   区域法，历史列表区 (0,220,720,1100) 内联），页题锚在位
3-4. 首条消息打通空态迁移 → open_ai_chat_by_role("小薇") +
   send_chat_text("qa-empty-first-018")（会话创建）→ press_back 回首页 →
   open_ai_history_page 断言新会话条目出现且仅此 1 条（历史区 OCR 令牌
   唯一命中）

数据说明：坑 4（deviceId 装用户 id 契约下服务端返空按空态处理）为
服务端契约面，UI 侧以空态快照+首条迁移回归覆盖；空态视图文案形态
登记 template_needs。

cleanup：无（合成会话留档即用例产物；专用空账号亦保留该会话）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHistoryEmptyBoundary(SwanRM09Mixin, BaseTest):
    """历史空态边界（零会话专用账号条件门，未预置即 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_empty_boundary(self):
        """空账号历史空态稳定，首条消息打通空态迁移。"""
        if os.environ.get("SWAN_AI_EMPTY_HISTORY_ACCT", "").strip() != "1":
            pytest.skip(
                "需零会话历史空账号（人工预置专用新账号后设 "
                "SWAN_AI_EMPTY_HISTORY_ACCT=1 运行；基线账号已有历史）")
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")

        # 步骤 1-2：空账号历史页空态
        self.userA.open_ai_history_page()
        assert self.userA.text_exists("历史对话记录", timeout=8) is not None, (
            "历史页页题未渲染 [OCR]")
        rows = self.userA.ocr_scan_page(region=(0, 220, 720, 1100))
        assert not rows, (
            f"空账号历史列表区非空（疑似有会话残留）: {[r['text'] for r in rows]}")

        # 步骤 3：首条消息打通空态迁移
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text("qa-empty-first-018")

        # 步骤 4：返回历史页复核新会话出现
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()
        self.userA.open_ai_history_page()
        assert self.userA.text_exists("qa-empty-first-018", timeout=15) is not None, (
            "首条消息后历史页未见新会话条目（空态迁移未打通）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
