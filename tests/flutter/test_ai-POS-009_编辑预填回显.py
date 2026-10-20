# CASE-ID: ai-POS-009
"""Swan 回归·AI 助手域：编辑角色分型预填回显·只读校验（ai-POS-009）。

步骤 → AW 映射：
1. 管理页定位预置测试角色 → open_ai_roles_page → 运行时条件门：
   暂未自定义角色 → skip（需人工预置自定义角色；基线账号必 skip）；
   预置角色名经 SWAN_AI_PRESET_ROLE 注入（默认 QA预置-角色），
   列表未命中该名 → skip（预置态与配置不一致）
2. 进入编辑分型 → click_text(角色名)（自定义角色行点击进编辑，
   /ai/role/create 同页编辑分型）→ 顶栏 自定义设置 锚
3-4. 校验昵称/提示词预填回显 → 顶部表单区 OCR 命中预置昵称；swipe_up
     后语音表单区上方提示词回显命中 SWAN_AI_PRESET_PROMPT（未配置则
     跳过提示词子断言——预填值以环境变量为准）
5. 不修改任何字段直接返回 → press_back（零保存零写）→ 角色列表回归

数据说明：只读校验零写（编辑分型预填现值，返回无保存提示）；
预填值口径=人工预置时登记的环境变量。

cleanup：无（零写；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRoleEditPrefillReadonly(SwanRM09Mixin, BaseTest):
    """编辑角色分型预填回显（只读校验，预置角色条件门）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_role_edit_prefill_readonly(self):
        """预置角色编辑分型预填回显正确，返回零写。"""
        role_name = os.environ.get("SWAN_AI_PRESET_ROLE", "").strip() or "QA预置-角色"
        prompt = os.environ.get("SWAN_AI_PRESET_PROMPT", "").strip()
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_roles_page()

        # 步骤 1：定位预置角色（条件门）
        if self.userA.find_text_by_ocr("暂未自定义角色", timeout=3) is not None:
            pytest.skip(
                "需人工预置自定义角色（基线账号暂未自定义角色）")
        if self.userA.find_text_by_ocr(role_name, timeout=5) is None:
            pytest.skip(
                f"预置角色「{role_name}」未在列表命中（预置态与 "
                f"SWAN_AI_PRESET_ROLE 配置不一致）")

        # 步骤 2：进入编辑分型（同页落地，零写入口）
        self.userA.click_text(role_name, timeout=8)
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "点击自定义角色后未落地角色编辑器 [OCR·顶栏区]")

        # 步骤 3：昵称预填回显（顶部表单区）
        assert self.userA.find_text_by_ocr(role_name, timeout=8) is not None, (
            f"编辑器昵称字段未见预填值「{role_name}」[OCR·表单区]")

        # 步骤 4：提示词预填回显（滚动后探测，未配置则跳过子断言）
        if prompt:
            self.userA.swipe_up()
            assert self.userA.find_text_by_ocr(prompt, timeout=8) is not None, (
                f"编辑器提示词字段未见预填值「{prompt}」[OCR·表单区]")

        # 步骤 5：不修改直接返回（零写）
        self.userA.press_back()
        assert self.userA.find_text_by_ocr(role_name, timeout=8) is not None, (
            "返回后角色列表未回归（编辑分型返回路径异常）[OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
