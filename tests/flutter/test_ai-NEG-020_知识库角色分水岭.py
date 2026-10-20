# CASE-ID: ai-NEG-020
"""Swan 回归·AI 助手域：官方知识库角色分水岭·无语音/实时/朗读（ai-NEG-020）。

步骤 → AW 映射：
1. 选中官方知识库角色（roleId==12 魔法数）进入聊天 → 前缀真实执行：
   open_ai_roles_page（所有角色页可达 + 系统 4 行锚回归）→ roleId==12
   角色卡位映射未标定（4 张系统角色卡 应用助手/好朋友/医生/云舒雁 与
   roleId 的对应关系 OCR 不可判定，YAML 亦未给出展示名）→ 运行时条件
   skip（template_needs 登记）
2-3. 无设备副标题/无实时入口/输出设备受限 → 模板补齐（卡位映射确认角色
     展示名）后：open_ai_chat_by_role(该角色) → 顶栏区 暂无设备 不出现
     （find_ai_topbar_text 反向探测）+ SWAN_AI_CHAT_VOICE_BTN 不出现
     （probe 反向）→ 输出设备弹层受限为只读浏览（零选择零写）

数据说明：坑 22 能力分水岭；isShared/chatCloseAudio 为协议推导面不在
UI 断言域；cleanup=返回默认角色（本用例只读进入，无默认态变更）。

cleanup：无（只读展示态；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiKnowledgeRoleBoundary(SwanRM09Mixin, BaseTest):
    """官方知识库角色分水岭（roleId==12 卡位映射未标定前条件 skip）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_knowledge_role_boundary(self):
        """所有角色页前缀可达后，roleId==12 卡位映射缺锚即条件 skip。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        # 前缀（真实执行）：所有角色页可达（roleId==12 角色卡的宿主页）
        self.userA.open_ai_roles_page()
        # 步骤 1：roleId==12 官方知识库角色卡位映射未标定，无法定位角色卡
        pytest.skip(
            "roleId==12 官方知识库角色卡位映射未标定（系统 4 卡 OCR 无对应"
            "关系，template_needs: roleId12 卡位映射）——补锚后转全自动")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
