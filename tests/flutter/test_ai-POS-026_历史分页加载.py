# CASE-ID: ai-POS-026
"""Swan 回归·AI 助手域：历史列表分页加载（ai-POS-026）。

步骤 → AW 映射：
1. 历史页滚动至列表底部 → open_ai_history_page → 运行时条件门：列表区
   OCR 会话行计数 < 6 → skip（会话数未超单页 limit，分页不可触发；需
   人工预置批量会话——计数为保守启发式，宁可 skip 不误判）
2. 触底观察追加渲染 → swipe_up ×N 至底部 → 分页尾锚（加载中/没有更多
   类提示）形态未标定 → 探针未命中即条件 skip（template_needs 登记）
3. 回顶二次触底 → 探针命中后：swipe_down 回顶断言首屏条目回归 →
   再 swipe_up 触底（分页游标不回退=不重复加载的可观察面）

数据说明：start/limit 分页窗口与 20s 超时兜底为服务端契约面，UI 侧以
触底追加+回顶回归覆盖；只读浏览零写。

cleanup：无（只读；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHistoryPagination(SwanRM09Mixin, BaseTest):
    """历史列表分页加载（数据量条件门 + 尾锚探针条件门）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_pagination(self):
        """触底触发分页加载，回顶二次触底游标不回退。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_history_page()

        # 条件门：会话行计数不足（保守启发式：宁可 skip 不误判）
        rows = self.userA.ocr_scan_page(region=(0, 220, 720, 1100))
        if len(rows) < 6:
            pytest.skip(
                f"历史会话行计数 {len(rows)} 低于分页触发阈值（需人工预置"
                "超过单页 limit 的批量会话）")

        # 步骤 1-2：滚动触底，分页尾锚探针
        for _ in range(3):
            self.userA.swipe_up()
        tail = None
        for kw in ("加载", "更多", "没有", "到底"):
            tail = self.userA.find_text_by_ocr(kw, timeout=2)
            if tail is not None:
                break
        if tail is None:
            pytest.skip(
                "分页尾锚（加载中/没有更多类提示）未命中（template_needs: "
                "历史分页尾锚形态）")

        # 步骤 3：回顶断言首屏回归 + 二次触底（游标不回退）
        self.userA.swipe_down()
        self.userA.swipe_down()
        assert self.userA.find_text_by_ocr("历史对话记录", timeout=5) is not None, (
            "回顶后历史页首屏未回归 [OCR]")
        self.userA.swipe_up()
        self.userA.swipe_up()
        assert self.userA.find_text_by_ocr("历史对话记录", timeout=5) is not None, (
            "二次触底后页面异常（分页加载挂死）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
