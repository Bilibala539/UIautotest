# CASE-ID: ai-POS-022
"""Swan 回归·AI 助手域：AI 回复接收渲染与多轮上下文保持（ai-POS-022）。

步骤 → AW 映射：
1. 发送首条消息 → mixin send_chat_text（用户气泡上屏断言内含）
2. 等待 AI 回复下行 → 先 ocr_scan_page 采集发送前内容区全量文本，再以
   mixin wait_ai_reply_bubble 轮询「内容区新增文本行」——AI 回复文案不可
   精确断言，以新增气泡文本行作为回复气泡出现并可读的可观察状态
   （传输层探针，非语义断言）；回复时效阈值 90s 为执行轮标定值
3. 第二条消息多轮上下文 → 追加发送后再次探测到新回复气泡（会话延续、
   无异常断线重连弹窗的页面级可观察面）
4. 服务端留档 → 退出经历史页核对首条消息文本出现在会话条目（名称/预览）

数据说明：YAML 中文提示词以 ASCII 等价文案替代（adb 中文注入不可达）。

cleanup：无（合成会话留档即用例产物；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiReplyBubbleStreaming(SwanRM09Mixin, BaseTest):
    """AI 回复气泡出现与多轮会话延续（可观察状态口径）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_ai_reply_bubble_appears(self):
        """发送两条消息，各自探测到 AI 回复气泡新增，历史页留档可见。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")

        # 发送前内容区快照（known 集合：既有气泡 + 问候语等）
        before = [item["text"] for item in self.userA.scan_ai_chat_content()]
        self.userA.send_chat_text("Please reply exactly with: OK")
        reply1 = self.userA.wait_ai_reply_bubble(before, timeout=90)
        assert reply1 is not None, (
            "发送首条消息后 90s 内内容区未出现新增文本行（AI 回复气泡未出现，"
            "回复时效边界需执行轮标定）[OCR·内容区]")

        # 多轮：第二条消息后再探测到新回复气泡
        self.userA.send_chat_text("What did I ask you to reply with just now")
        reply2 = self.userA.wait_ai_reply_bubble(
            before + [reply1,
                      "Please reply exactly with: OK",
                      "What did I ask you to reply with just now"], timeout=90)
        assert reply2 is not None, (
            "发送第二条消息后 90s 内未再出现新增回复气泡（多轮会话中断）[OCR·内容区]")

        # 服务端留档：历史页会话条目可见本次消息
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()
        self.userA.open_ai_history_page()
        assert self.userA.assert_any_text(
            ("Please reply exactly", "What did I ask"), timeout=10), (
            "历史页未见本次会话条目（首条/次条消息均未留档）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
