# CASE-ID: ai-POS-025
"""Swan 回归·AI 助手域：历史会话恢复进入对话页（ai-POS-025）。

步骤 → AW 映射：
1. 预置会话 → go_top_tab("AI") + open_ai_chat_by_role("小薇") +
   mixin send_chat_text 发送 ASCII 令牌（会话名=首条用户消息，wave5 实测
   'play a song' → 历史行 'playa song' 口径）→ press_back 回画廊
2. 历史页点击该会话 → mixin open_ai_history_page + click_text(令牌)
3. 恢复进入对话页 → mixin assert_chat_token(令牌)（内容区命中历史消息
   文本 = 上下文恢复）+ 「发送消息」输入框就绪（可继续会话的可观察面）
4. 退出 → press_back 逐级返回画廊锚

数据说明：AI 回复内容不可精确断言，恢复验证落在「历史消息文本回显 +
输入框就绪」可观察状态；令牌含连字符，OCR 对符号容忍度执行轮核实，
见 report.template_needs。

cleanup：无（合成会话留档即用例产物；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHistorySessionRestore(SwanRM09Mixin, BaseTest):
    """历史会话恢复进入对话页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_session_restore(self):
        """点击历史会话恢复上下文：历史消息回显且输入框就绪。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")

        # 预置：发送令牌消息生成可定位会话
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text("qa-restore-0777")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 历史页点击该会话恢复
        self.userA.open_ai_history_page()
        self.userA.click_text("qa-restore-0777", timeout=10)
        self.userA.assert_chat_token("qa-restore-0777")
        assert self.userA.text_exists("发送消息", timeout=10) is not None, (
            "恢复会话后输入框未就绪（未见「发送消息」占位）[OCR]")

        # 退出（对话页 → 历史页/首页逐级）
        self.userA.press_back()
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
