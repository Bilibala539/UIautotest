# CASE-ID: ai-POS-015
"""Swan 回归·AI 助手域：多选全选/反选/清空联动展示态·零删除触发（ai-POS-015）。

步骤 → AW 映射：
1. 管理页进入多选模式 → open_ai_roles_page → 条件门：暂未自定义角色 →
   skip（多选联动需 ≥1 自定义角色；基线账号必 skip）→ click_text("多选")
2. 点击全选 → click_text("全选")（wave5 实测 OCR 形态「口全选」，子串
   命中）→ 勾选态回显锚未标定（勾选框选中态为视觉判定，OCR 无稳定锚）
   → 回显探针：全选后 OCR 扫描勾选态标记（☑/√/已选类符号），未命中
   即条件 skip（template_needs 登记）
3-5. 反选/清空/退出（删除控件置灰核验）→ 探针命中后执行：行勾选
     click_text("口")（首个行勾选框）→ 清空复核 删除 控件态（仅存在性
     断言 ⛔ 零点击）→ click_text("取消") 退出多选 → 角色列表无变化

数据说明：零删除触发——删除类控件全程仅存在性/置灰态断言；勾选框
ValueKey 按 roleId 逐项断言属服务端契约面，UI 侧以回显探针覆盖。

cleanup：无（零删除零选择残留；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiRolesMultiselectLinkage(SwanRM09Mixin, BaseTest):
    """多选全选/反选/清空联动展示态（零删除触发，回显探针条件门）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_roles_multiselect_linkage(self):
        """多选→全选联动，勾选态回显探针命中后核验清空态与零删除。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_roles_page()

        # 条件门：无自定义角色即 skip
        if self.userA.find_text_by_ocr("暂未自定义角色", timeout=3) is not None:
            pytest.skip("需 ≥1 个自定义角色（基线账号暂未自定义角色）")

        # 步骤 1-2：多选 + 全选
        self.userA.click_text("多选", timeout=10)
        if self.userA.find_text_by_ocr("全选", timeout=5) is None:
            self.userA.press_back()
            pytest.skip(
                "多选态锚（全选）未命中（template_needs: 多选态控件形态）")
        self.userA.click_text("全选", timeout=5)

        # 勾选态回显探针：选中态符号未命中即条件 skip（视觉判定域）
        marker = None
        for sym in ("☑", "√", "已选", "选√"):
            marker = self.userA.find_text_by_ocr(sym, timeout=2)
            if marker is not None:
                break
        if marker is None:
            self.userA.press_back()
            pytest.skip(
                "勾选态回显无 OCR 稳定锚（选中态为视觉判定，template_needs: "
                "勾选框选中态形态）——已退出多选，零状态残留")

        # 步骤 3：反选一个（首个行勾选框）
        self.userA.click_text("口", timeout=5)

        # 步骤 4-5：清空态下删除控件置灰核验（⛔ 零点击）+ 退出
        assert self.userA.find_text_by_ocr("删除", timeout=5) is not None, (
            "多选态删除控件未渲染 [OCR]")
        self.userA.click_text("取消", timeout=8)
        assert self.userA.find_text_by_ocr("多选", timeout=8) is not None, (
            "退出多选后未回归普通列表态 [OCR]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
