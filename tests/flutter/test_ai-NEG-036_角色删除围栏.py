# CASE-ID: ai-NEG-036
"""Swan 回归·AI 助手域：角色删除围栏·弹窗即止取消分支（ai-NEG-036）。

步骤 → AW 映射（默认执行止于步骤 3 取消分支——禁区 2 真删除不执行）：
0. 前置条件门 → open_ai_roles_page：若 暂未自定义角色 → skip（需人工
   预置 ≥3 一次性合成角色；基线账号无自定义角色必 skip，真删除风险
   天然隔离在专用预置账号）
1. 勾选角色 → 多选态：click_text("多选") → click_text("全选")
   （勾选框 ai-role-checkbox-{roleId} 逐项锚未标定，以全选勾选进围栏，
   单行勾选锚登记 template_needs）
2. 点击删除 → click_text("删除")（⛔ 弹窗出现即止）
3. 取消 → find_text_by_ocr("取消") → click_text("取消") → 断言多选态
   回归（全选仍在）；找不到取消则 press_back 兜底关弹层并 skip 登记
   弹层形态
4. 复核角色仍在 → 退出多选（press_back）→ 预置角色名仍在列表
   （SWAN_AI_PRESET_ROLE，默认 QA预置-角色；未命中即 fail——围栏泄露）

数据说明：禁区 2——服务端物理删除无 undo，本用例全程零确认点击；
「修改成功」toast 文案怪点属真删除轮（主对话单独授权）不在默认范围。

cleanup：无（零删除；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRoleDeleteFence(SwanRM09Mixin, BaseTest):
    """角色删除围栏：弹窗即止、取消分支（零删除触发）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_role_delete_fence_cancel(self):
        """多选全选→删除→弹窗取消→复核角色仍在（零服务端写）。"""
        role_name = os.environ.get("SWAN_AI_PRESET_ROLE", "").strip() or "QA预置-角色"
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_roles_page()

        # 前置条件门：无自定义角色即 skip（人工预置 ≥3 一次性合成角色）
        if self.userA.find_text_by_ocr("暂未自定义角色", timeout=3) is not None:
            pytest.skip(
                "需人工预置 ≥3 个一次性合成角色（基线账号暂未自定义角色）")

        # 步骤 1：多选态 + 全选勾选（单行勾选锚未标定，以全选进围栏）
        self.userA.click_text("多选", timeout=10)
        if self.userA.find_text_by_ocr("全选", timeout=5) is None:
            self.userA.press_back()
            pytest.skip(
                "多选态勾选锚（全选/行勾选框）未命中（template_needs: "
                "ai-role-checkbox 逐项锚）——形态执行轮标定后转全自动")
        self.userA.click_text("全选", timeout=5)

        # 步骤 2：点击删除——弹窗出现即止（⛔ 零确认点击）
        self.userA.click_text("删除", timeout=8)

        # 步骤 3：取消分支（围栏默认出口）
        if self.userA.find_text_by_ocr("取消", timeout=5) is None:
            self.userA.press_back()
            pytest.skip(
                "删除确认弹层未见「取消」项（弹层形态需执行轮标定，"
                "template_needs: 删除确认弹层）——已按返回键兜底关弹层")
        self.userA.click_text("取消", timeout=5)
        assert self.userA.find_text_by_ocr("全选", timeout=8) is not None, (
            "取消后未回到多选态（围栏取消分支异常）[OCR]")

        # 步骤 4：退出多选复核角色仍在（围栏零泄露）
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(role_name, timeout=8) is not None, (
            f"取消删除后预置角色「{role_name}」从列表消失（发生非预期删除）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
