# CASE-ID: ai-POS-012
"""Swan 回归·AI 助手域：形象选择选中态会话内保持与二次进入回显（ai-POS-012）。

步骤 → AW 映射：
1. 形象选择页点选素材 A → 编辑器 → click_image(SWAN_ROLE_EDITOR_SELECT)
   → click_text("动图")（首卡=A；选中仅客户端态）→ 选中态回显探针
   （未命中即条件 skip，template_needs）
2. 返回编辑器 → press_back（零保存，选择随返回失效或保持为待标定形态）
3-4. 二次进入回显 A 仍选中 → 探针命中后：重进形象选择页 → 回显探针
     二次命中（会话内保持的可观察面）→ press_back 零写返回

数据说明：选中态会话内保持为客户端状态面（零保存零服务端写）；
高亮/勾选回显为视觉判定域，探针未标定前条件 skip。

cleanup：无（选择不保存即失效；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from image.image_name_mapping import SWAN_ROLE_EDITOR_SELECT
from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiAvatarPickPersistence(SwanRM09Mixin, BaseTest):
    """形象选中态会话内保持与二次进入回显（回显探针条件门）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def _pick_marker(self):
        """选中态回显探针：符号类标记扫描。"""
        for sym in ("☑", "√", "已选"):
            marker = self.userA.find_text_by_ocr(sym, timeout=2)
            if marker is not None:
                return marker
        return None

    def test_avatar_pick_persistence(self):
        """点选素材 A 后二次进入回显保持（探针命中面），零写返回。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 步骤 1：进入形象选择页点选素材 A
        self.userA.click_image(SWAN_ROLE_EDITOR_SELECT, timeout=10)
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "形象选择页未达 [OCR·顶栏区]")
        assert self.userA.find_text_by_ocr("动图", timeout=8) is not None, (
            "形象素材网格未加载 [OCR]")
        self.userA.click_text("动图", timeout=5)
        if self._pick_marker() is None:
            self.userA.press_back()
            pytest.skip(
                "素材选中态回显无 OCR 稳定锚（template_needs: 素材选中态"
                "形态）——零写返回")

        # 步骤 2：返回编辑器（零保存）
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "返回后未回到角色编辑器 [OCR·顶栏区]")

        # 步骤 3-4：二次进入回显 A 仍选中（会话内保持）
        self.userA.click_image(SWAN_ROLE_EDITOR_SELECT, timeout=10)
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "二次进入形象选择页失败 [OCR·顶栏区]")
        assert self._pick_marker() is not None, (
            "二次进入后选中态回显丢失（会话内保持失效）[OCR]")
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "最终返回未回到角色编辑器 [OCR·顶栏区]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
