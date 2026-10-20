# CASE-ID: ai-NEG-002
"""Swan 回归·AI 助手域：实时页快速连点返回防 PopScope 死循环（ai-NEG-002）。

步骤 → AW 映射：
1. 从聊天页点击实时通话入口 → 前缀真实执行：ensure_logged_in_on_home +
   go_top_tab("AI") + open_ai_chat_by_role("小薇")（对话页可达性每轮验证）
   → 入口 ai_chat_realtime_action 为无文案图标（顶栏图标群 OCR 无锚，
   模板未截取且本批次禁改 image_name_mapping.py）→ 运行时条件 skip
2-4. 转场前后快速连点返回/重进/再退 → 依赖步骤 1 入口，模板补齐后
     （package_report.template_needs 登记）本用例转全自动；连点用
     press_key("back") 序列实现（转场期快速触发）

数据说明：禁区 1——通话建立前即退出，零计费时长；专用受控账号口径
（基线账号执行时同样止于条件 skip，不产生通话）。

cleanup：无（未进入通话页；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRealtimeRapidBack(SwanRM09Mixin, BaseTest):
    """实时页快速连点返回——防 PopScope 死循环（入口图标未截取前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_realtime_rapid_back_no_deadloop(self):
        """对话页前缀可达后，实时入口图标缺模板即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：对话页可达 = 步骤 1 的前置半步
        self.userA.open_ai_chat_by_role("小薇")
        # 步骤 1 点击实时通话入口：ai_chat_realtime_action 为无文案图标
        pytest.skip(
            "实时通话入口为无文案图标（顶栏图标群 OCR 无锚），图标模板未截取"
            "（template_needs: ai_chat_realtime_action）——补模板后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
