# CASE-ID: ai-POS-023
"""Swan 回归·AI 助手域：历史页新建会话入口开启新聊天（ai-POS-023）。

步骤 → AW 映射：
1. 历史页点击新建聊天入口 → 前缀真实执行：open_ai_history_page
   （AI 首页历史入口路径，与聊天页入口同落 /ai/history）→ 入口
   ai_history_create_new_chat 为无文案图标（历史页 OCR 无锚，模板未截取）
   → 运行时条件 skip
2-4. 新会话初始态/首条消息/发送建会话 → 模板补齐后：click_image(新建) →
     assert 发送消息就绪（空会话无历史消息渲染）→ send_chat_text(令牌)
     （回显+上屏+输入框清空）→ open_ai_history_page 断言新会话出现
     （与 ai-POS-024 联动核对）

数据说明：pushReplacement 替换（历史页被聊天页替换不叠栈）由返回路径
回归（单次 back 落 AI 首页而非历史页）。

cleanup：会话数据留基线账号（合成会话留档即用例产物）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiHistoryNewChatEntry(SwanRM09Mixin, BaseTest):
    """历史页新建会话入口开启新聊天（入口图标未截取前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_new_chat_entry(self):
        """历史页前缀可达后，新建聊天图标缺模板即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：历史页可达（新建入口的宿主页）
        self.userA.open_ai_history_page()
        # 步骤 1：ai_history_create_new_chat 无文案图标，模板未截取
        pytest.skip(
            "历史页新建聊天入口为无文案图标（历史页 OCR 无锚），图标模板"
            "未截取（template_needs: ai_history_create_new_chat）"
            "——补模板后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
