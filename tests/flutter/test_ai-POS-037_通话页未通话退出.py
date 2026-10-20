# CASE-ID: ai-POS-037
"""Swan 回归·AI 助手域：通话页未通话态正常退出·PopScope 正向路径（ai-POS-037）。

步骤 → AW 映射：
1-5. 通话页返回退出/回聊天页复核/二次进出/播放器让位恢复 → 全部依赖
     ai_chat_realtime_action 无文案图标入口（模板未截取）。
     前缀真实执行：对话页可达（退出的落点页）→ 运行时条件 skip。
     模板补齐后：进入 → press_back 退出（leave 短路正向路径）→
     assert 对话页恢复（发送消息锚）→ 二次进出 → 播放器让位恢复
     （SWAN_AI_PLAY_PRESET=1 时经 preset_playing_on_favorite 预置在播
     后核对播放条回归）。

数据说明：禁区 1——未通话态退出（leave 短路），零计费；PopScope
canPop=false 死循环坑（M09-P12）的正向对照面。

cleanup：无（未进入通话页；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRealtimeExitNormal(SwanRM09Mixin, BaseTest):
    """通话页未通话态正常退出（入口图标未截取前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_realtime_exit_normal(self):
        """对话页前缀可达后，实时入口图标缺模板即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：退出落点的对话页可达
        self.userA.open_ai_chat_by_role("小薇")
        # 步骤 1：进入通话页依赖 ai_chat_realtime_action 无文案图标
        pytest.skip(
            "实时通话入口为无文案图标（对话页 OCR 无锚），图标模板未截取"
            "（template_needs: ai_chat_realtime_action）——补模板后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
