# CASE-ID: ai-POS-024
"""Swan 回归·AI 助手域：历史会话列表加载与条目渲染（ai-POS-024）。

步骤 → AW 映射：
1. 进入历史页（AI 首页历史入口，与聊天页历史入口同落 /ai/history）
   → go_top_tab("AI") + mixin open_ai_history_page（顶栏页题锚）
2-3. 会话列表加载与一致性 → 预置：先在「小薇」对话页经 send_chat_text 发送
     ASCII 令牌消息（chat→history 为 pushReplacement 语义，令牌作为会话名/
     预览落列表），返回后进历史页断言令牌条目渲染（名称/预览其一可见）
4. 返回退出历史页 → press_back 回 AI 首页画廊锚

数据说明：会话条目以自身发送的 ASCII 令牌可精确定位（wave5 实测会话行=
会话名+预览两行文本）。

cleanup：无（合成会话留档即用例产物；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHistoryListRendering(SwanRM09Mixin, BaseTest):
    """历史会话列表加载与条目渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_list_renders_token_session(self):
        """发送令牌消息后历史页渲染该会话条目。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")

        # 预置：发送令牌消息生成可定位会话
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text("qa-hist-list-1024")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 历史页：条目渲染（令牌出现在会话名或预览）
        self.userA.open_ai_history_page()
        assert self.userA.text_exists("qa-hist-list-1024", timeout=15) is not None, (
            "历史页未见刚发送的令牌会话条目（列表未加载或条目命名口径需标定）[OCR]")

        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
