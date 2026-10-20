# CASE-ID: ai-POS-036
"""Swan 回归·AI 助手域：通话页 UI 元素存在性断言·零 Key 兜底（ai-POS-036）。

步骤 → AW 映射：
1-4. 退出/字幕区/静音控件存在性 → 通话页全页零 Key（YAML 溯源明示
     ai_realtime_call_page 零 Key），控件形态执行轮记录后补锚点清单；
     进入通话页依赖 ai_chat_realtime_action 无文案图标（模板未截取）。
     前缀真实执行：对话页可达 → 运行时条件 skip。
     控件存在性在模板补齐后以 OCR/图像双锚实现（退出控件/字幕区容器/
     状态控件），全程零点击（禁区 1：零采集零通话）。

数据说明：本用例 YAML 自带"形态执行轮记录，供后续轮补锚点清单"口径，
template_needs 登记 ai_chat_realtime_action + 通话页控件三项形态。

cleanup：无（未进入通话页；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRealtimePageUiElements(SwanRM09Mixin, BaseTest):
    """通话页 UI 元素存在性（入口图标未截取前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_realtime_page_ui_elements(self):
        """对话页前缀可达后，实时入口图标缺模板即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：普通角色对话页可达（进入通话页的唯一路径）
        self.userA.open_ai_chat_by_role("小薇")
        # 通话页全页零 Key，控件锚待执行轮标定；入口图标模板未截取
        pytest.skip(
            "通话页依赖 ai_chat_realtime_action 无文案图标入口（模板未截取）"
            "且通话页控件形态待执行轮标定（template_needs: ai_chat_realtime_"
            "action + 通话页退出/字幕区/静音控件）——补锚后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
