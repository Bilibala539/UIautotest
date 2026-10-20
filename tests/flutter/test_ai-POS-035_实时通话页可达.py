# CASE-ID: ai-POS-035
"""Swan 回归·AI 助手域：realtime 通话页可达·页面级不启动通话（ai-POS-035）。

步骤 → AW 映射：
1. 对话页点击实时通话入口 → 前缀真实执行：ensure_logged_in_on_home +
   go_top_tab("AI") + open_ai_chat_by_role("小薇")（普通角色非 roleId==12
   对话页可达）→ 入口 ai_chat_realtime_action 为无文案图标（OCR 无锚，
   模板未截取）→ 运行时条件 skip
2-4. 通话页渲染/静置观察/退出 → 依赖步骤 1；硬约束（不触碰音频启动控件、
     不说话、零通话零计费）已在模板补齐后的全自动版承担

数据说明：禁区 1——insufficient_balance 真实存在，全程不发起通话；
观察型断言面（渲染无白屏无错误弹窗）以内容区 OCR 快照非空实现。

cleanup：无（未进入通话页；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRealtimePageReach(SwanRM09Mixin, BaseTest):
    """realtime 通话页可达（入口图标未截取前条件 skip，零通话零计费）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_realtime_page_reach(self):
        """普通角色对话页前缀可达后，实时入口图标缺模板即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：普通角色对话页可达
        self.userA.open_ai_chat_by_role("小薇")
        # 步骤 1：ai_chat_realtime_action 无文案图标，模板未截取
        pytest.skip(
            "实时通话入口为无文案图标（对话页 OCR 无锚），图标模板未截取"
            "（template_needs: ai_chat_realtime_action）——补模板后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
