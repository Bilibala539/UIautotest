# CASE-ID: ai-POS-018
"""Swan 回归·AI 助手域：官方知识库角色能力边界展示态（ai-POS-018）。

步骤 → AW 映射：
1. AI 首页定位官方知识库角色卡 → 前缀真实执行：open_ai_roles_page
   （角色卡宿主页可达）→ roleId==12 角色卡位映射未标定 → 运行时条件
   skip（与 ai-NEG-020 同因，独立用例独立登记）
2-4. 进入对话页/断言语音入口不出现/断言实时入口与设备副标题不出现 →
     模板补齐后：open_ai_chat_by_role(该角色) → SWAN_AI_CHAT_VOICE_BTN
     反向探测不存在 + 顶栏区 暂无设备 反向不存在（find_ai_topbar_text
     配合 find_text_by_ocr 反向）——反向断言面均有既有锚，仅卡位待标定

数据说明：坑 22 分水岭展示态（无语音输入/无实时入口/无设备副标题）；
chatCloseAudio 为协议推导不在 UI 断言域；只读展示零写。

cleanup：无（只读展示态；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiKnowledgeRoleTraits(SwanRM09Mixin, BaseTest):
    """官方知识库角色能力边界展示态（卡位映射未标定前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_knowledge_role_traits(self):
        """所有角色页前缀可达后，roleId==12 卡位映射缺锚即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：所有角色页可达
        self.userA.open_ai_roles_page()
        # 步骤 1：roleId==12 角色卡位映射未标定
        pytest.skip(
            "roleId==12 官方知识库角色卡位映射未标定（template_needs: "
            "roleId12 卡位映射）——补锚后转全自动（反向断言锚已备）")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
