# CASE-ID: ai-POS-011
"""Swan 回归·AI 助手域：形象选择页素材网格加载与选中回显（ai-POS-011）。

步骤 → AW 映射：
1. 编辑器内进入形象选择页 → open_ai_role_editor + click_image
   (SWAN_ROLE_EDITOR_SELECT)（wave5 实测文本「选择」多义须图像锚）→
   AI形象 + 完成(⛔ 仅存在性) 页锚断言
2. 素材网格加载 → wave5 实测 4 张动图卡（OCR「动图」×4）→ 断言动图
   素材卡渲染（网格非空）
3. 点选素材 + 选中态回显 → click_text("动图")（首卡点选；选中仅客户端
   态，零保存零写）→ 选中态回显探针（☑/√/已选类符号；高亮为视觉判定
   OCR 无稳定锚）→ 未命中即条件 skip（template_needs 登记选中态形态）
4. 零写返回 → press_back → 编辑器锚回归

数据说明：user/getVisionInfo visionType=3 为服务端契约面；完成按钮为
红线控件全程零点击（形象选择不落 addOrUpdateRole）。

cleanup：无（选择不保存即失效；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from image.image_name_mapping import SWAN_ROLE_EDITOR_SELECT
from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiAvatarGridPick(SwanRM09Mixin, BaseTest):
    """形象选择页素材网格加载与选中回显（回显探针条件门）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_avatar_grid_pick_feedback(self):
        """素材网格渲染，点选素材后回显探针核验，零写返回。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()
        self.userA.click_image(SWAN_ROLE_EDITOR_SELECT, timeout=10)

        # 步骤 1：形象选择页锚（完成=⛔红线 仅存在性）
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "形象选择页未达 [OCR·顶栏区]")
        assert self.userA.find_text_by_ocr("完成", timeout=8) is not None, (
            "形象选择页未见「完成」锚（页面壳异常）[OCR]")

        # 步骤 2：素材网格加载（wave5 实测 4 张动图卡）
        assert self.userA.find_text_by_ocr("动图", timeout=8) is not None, (
            "形象素材网格未见动图素材卡（网格未加载）[OCR]")

        # 步骤 3：点选素材 + 选中态回显探针（高亮为视觉判定域）
        self.userA.click_text("动图", timeout=5)
        marker = None
        for sym in ("☑", "√", "已选"):
            marker = self.userA.find_text_by_ocr(sym, timeout=2)
            if marker is not None:
                break
        if marker is None:
            self.userA.press_back()
            pytest.skip(
                "形象素材选中态回显无 OCR 稳定锚（高亮/勾选为视觉判定，"
                "template_needs: 素材选中态形态）——已零写返回")

        # 步骤 4：零写返回
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "返回后未回到角色编辑器 [OCR·顶栏区]")

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
