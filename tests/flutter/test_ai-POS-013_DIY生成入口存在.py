# CASE-ID: ai-POS-013
"""Swan 回归·AI 助手域：DIY 页可达与生成入口存在性（零惠币）（ai-POS-013）。

步骤 → AW 映射：
1. 形象选择页进入 DIY 页 → go_top_tab("AI") + open_ai_role_editor() +
   click_image(SWAN_ROLE_EDITOR_SELECT)（AI 形象页锚）+
   click_image(SWAN_ROLE_IMAGES_DIY_BTN)（DIY形象页锚）
2. 素材选择区渲染 → 断言「上传照片」「选择风格」
3. 生成提交入口存在性（仅存在性，零点击——⛔ generateMedia 消耗惠币
   0.2 惠币/图，禁区 1）→ 断言「开始生成」+ 计费文案「0.2惠币」+「充值」
   （仅 OCR 存在性，绝不点击）
4. 返回退出 → press_back 回 AI 形象页（页题锚——无生成任务残留的页面级
   可观察面）

cleanup：无（全程零生成接口触发，0 惠币消耗；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_ROLE_EDITOR_SELECT,
    SWAN_ROLE_IMAGES_DIY_BTN,
)
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiDiyEntryExistence(SwanRM09Mixin, BaseTest):
    """DIY 页可达与生成入口存在性（零惠币）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_diy_entry_existence(self):
        """DIY 页落地，素材区与生成入口（仅存在性）渲染，返回无残留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()
        self.userA.click_image(SWAN_ROLE_EDITOR_SELECT, timeout=10)
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "选择按钮点击后未落地「AI形象」页 [OCR·顶栏区]")
        self.userA.click_image(SWAN_ROLE_IMAGES_DIY_BTN, timeout=10)
        assert self.userA.find_ai_topbar_text("DIY形象", timeout=10) is not None, (
            "DIY形象按钮点击后未落地「DIY形象」页 [OCR·顶栏区]")

        # 素材选择区 + 生成入口存在性（零点击）
        assert self.userA.text_exists("上传照片", timeout=8) is not None, (
            "DIY 页素材选择区「上传照片」缺失 [OCR]")
        assert self.userA.text_exists("选择风格", timeout=8) is not None, (
            "DIY 页素材选择区「选择风格」缺失 [OCR]")
        assert self.userA.text_exists("开始生成", timeout=8) is not None, (
            "DIY 页生成提交入口「开始生成」缺失 [OCR]")  # ⛔ 仅存在性，绝不点击
        assert self.userA.text_exists("0.2惠币", timeout=8) is not None, (
            "DIY 页计费文案「0.2惠币」未渲染 [OCR]")
        assert self.userA.text_exists("充值", timeout=8) is not None, (
            "DIY 页「充值」入口缺失 [OCR]")  # ⛔ 仅存在性，绝不点击

        # 返回形象选择页（无生成任务残留的页面级可观察面）
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "DIY 页返回后未回到「AI形象」页 [OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
