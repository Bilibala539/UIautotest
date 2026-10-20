# CASE-ID: ai-POS-041
"""Swan 回归·AI 助手域：空历史列表展示与新建会话入口（ai-POS-041）。

步骤 → AW 映射：
1. 空历史账号进入历史对话页 → 运行时条件门 SWAN_AI_EMPTY_HISTORY_ACCT=1
   （与 ai-NEG-018 同一账号口径；基线账号有历史会话，空态不成立即
   skip）→ open_ai_history_page
2. 断言无历史会话展示空态 → 历史列表区 (0,220,720,1100) OCR 快照
   为空断言（空态可观察面）
3. 断言新建会话入口存在 → 新建聊天入口为无文案图标（顶栏图标簇 OCR
   呈乱码，无文本锚）→ 探针 OCR 扫描 新建/新对话 类文本，未命中即
   条件 skip（template_needs 登记图标模板 ai_history_create_new_chat）

数据说明：空态展示为服务端会话列表契约面；新建入口点击进入新会话
页为后续用例域，本用例止步入口存在性（零点击）。

cleanup：无（零新建零写；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiEmptyHistoryEntry(SwanRM09Mixin, BaseTest):
    """空历史列表展示与新建会话入口（空账号条件门+图标探针）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_empty_history_new_entry(self):
        """空历史账号列表为空，新建入口存在性核验（零点击）。"""
        if os.environ.get("SWAN_AI_EMPTY_HISTORY_ACCT", "").strip() != "1":
            pytest.skip(
                "需空历史会话账号前置（rig 环境 SWAN_AI_EMPTY_HISTORY_ACCT=1；"
                "基线账号已有历史会话，空态不成立）")
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_history_page()

        # 步骤 2：历史列表区为空（空态展示）
        rows = self.userA.ocr_scan_page(region=(0, 220, 720, 1100))
        assert not rows, (
            f"空历史账号列表区仍有会话行（{len(rows)} 行）[OCR·列表区]")

        # 步骤 3：新建会话入口存在性探针（无文案图标，形态待标定）
        entry = None
        for kw in ("新建", "新对话"):
            entry = self.userA.find_text_by_ocr(kw, timeout=2)
            if entry is not None:
                break
        assert entry is not None, (
            "新建会话入口为无文案图标（顶栏图标簇 OCR 无锚），图像模板"
            "未截取（template_needs: ai_history_create_new_chat）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
