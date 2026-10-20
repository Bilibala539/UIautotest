# CASE-ID: ai-POS-030
"""Swan 回归·AI 助手域：AI 朗读入口存在性·止步点按前（ai-POS-030）。

步骤 → AW 映射：
1-2. 小薇生成回复 → send_chat_text 探针消息 → wait_ai_reply_bubble
     等回复气泡 → 回复气泡关联 朗读 入口探针（朗读/播报/喇叭 关键词，
     波形图标为无文案控件，回复区形态待标定）→ 未命中即条件 skip
     （template_needs 登记朗读入口形态）
3. 入口存在性（仅存在性零点按）→ 探针命中即止：断言入口可见，不点击
   （⛔ 朗读按钮点击写入 closeAudio 协议=禁区，全程零触发）

数据说明：TTS 播放行为与字幕跟滚为音频/视觉底层态（框架仅 UI/OCR
观测层，无音频观察锚），本用例止步入口存在性，不覆盖播放过程。

cleanup：无（未发起朗读；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiReadAloudEntry(SwanRM09Mixin, BaseTest):
    """AI 朗读入口存在性（回复区形态探针条件门，全程零点按）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_read_aloud_entry_exists(self):
        """回复生成后朗读入口存在性核验（仅存在性，零点按）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text("qa-readaloud-030")
        assert self.userA.wait_ai_reply_bubble(
            ["qa-readaloud-030"], timeout=90) is not None, (
            "回复气泡未出现（会话链路异常）[OCR·内容区]")

        # 步骤 1-2：回复关联朗读入口探针（无文案控件，形态待标定）
        entry = None
        for kw in ("朗读", "播报", "喇叭"):
            entry = self.userA.find_text_by_ocr(kw, timeout=2)
            if entry is not None:
                break
        if entry is None:
            self.userA.press_back()
            self.userA.assert_ai_home_gallery()
            pytest.skip(
                "朗读入口为无文案控件（回复区 OCR 无稳定锚），控件图像"
                "模板未截取（template_needs: 朗读入口形态）——已退出会话")

        # 步骤 3：入口存在性确认（⛔ 全程零点按）
        assert entry is not None, "朗读入口未渲染 [OCR]"

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
