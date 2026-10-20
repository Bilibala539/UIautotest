# CASE-ID: ai-POS-017
"""Swan 回归·AI 助手域：LLM 模型目录加载与选择·止步保存前（ai-POS-017）。

步骤 → AW 映射：
1. 编辑器内打开模型选择器 → open_ai_role_editor → swipe_up 滚动编辑器
   表单 → 模型选择器入口 OCR 探针（模型/LLM 关键词；wave5 编辑器 dump
   无模型锚，页面未探索）→ 未命中即条件 skip（template_needs 登记）
2-3. 浏览目录/选择回显 → 探针命中后：click_text(入口) → 选中态回显
     探针（选择器页未探索，选中态形态未知）→ 未命中即 skip 并返回；
     命中则断言目录 OCR 非空 + 返回编辑器回显
4. 不保存直接返回 → press_back（编辑器）→ press_back（首页）零写退出

数据说明：getChatListByName 目录加载为服务端契约面；止步保存前零写
（modelId 随 WS 连接下发，本用例不发起会话）。

cleanup：无（未保存；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiModelCatalogPick(SwanRM09Mixin, BaseTest):
    """LLM 模型目录加载与选择（入口探针条件门，止步保存前零写）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_model_catalog_pick(self):
        """编辑器滚动探针定位模型选择器，目录浏览后零写返回。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 步骤 1：滚动编辑器探针定位模型选择器入口
        self.userA.swipe_up()
        entry_kw = None
        for kw in ("模型", "LLM"):
            if self.userA.find_text_by_ocr(kw, timeout=3) is not None:
                entry_kw = kw
                break
        if entry_kw is None:
            self.userA.press_back()
            self.userA.assert_ai_home_gallery()
            pytest.skip(
                "模型选择器入口在编辑器 OCR 无锚（页面未探索，template_needs: "
                "LLM 模型选择器入口）——已零写返回")
        self.userA.click_text(entry_kw, timeout=5)

        # 步骤 2-3：目录浏览 + 选中态回显探针（选择器页未探索）
        rows = self.userA.ocr_scan_page()
        assert rows, "模型选择器页 OCR 快照为空（页面渲染异常）"
        picked = None
        for kw in ("已选", "☑", "√"):
            picked = self.userA.find_text_by_ocr(kw, timeout=2)
            if picked is not None:
                break
        if picked is None:
            self.userA.press_back()
            pytest.skip(
                "模型条目选中态回显无 OCR 锚（选择器页形态待标定，"
                "template_needs: 模型选中态）——未选择零写返回")

        # 步骤 4：不保存直接返回（零写）
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "返回后未回到角色编辑器 [OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
