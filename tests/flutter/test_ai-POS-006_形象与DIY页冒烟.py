# CASE-ID: ai-POS-006
"""Swan 回归·AI 助手域：形象选择页与 DIY 页冒烟可达（ai-POS-006）。

步骤 → AW 映射：
1. AI 首页进入角色编辑器（新建分型）→ go_top_tab("AI") +
   mixin open_ai_role_editor()
2. 编辑器进入形象选择页 → click_image(SWAN_ROLE_EDITOR_SELECT)，
   到位断言顶栏页题「AI形象」+ 完成（⛔ 仅存在性，绝不点击）
3. 形象选择页进入 DIY 页 → click_image(SWAN_ROLE_IMAGES_DIY_BTN)
   （页面题与底部按钮同名「DIY形象」，OCR 自上而下会命中页题，故走 [图]），
   到位断言页题「DIY形象」+ 上传照片/选择风格
4. 逐级返回 → press_back 回 AI 形象页（页题锚）→ press_back 回编辑器
   （自定义设置锚）→ press_back 回 AI 首页（画廊锚）——无卡死无叠栈

cleanup：无（零 Key 页面只读冒烟，零生成零惠币；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_ROLE_EDITOR_SELECT,
    SWAN_ROLE_IMAGES_DIY_BTN,
)
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiImagesAndDiyPagesSmoke(SwanRM09Mixin, BaseTest):
    """形象选择页与 DIY 页冒烟可达（零 Key）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_images_and_diy_pages_smoke(self):
        """编辑器 → AI 形象页 → DIY 页逐级可达并逐级返回。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()

        # 形象选择页
        self.userA.click_image(SWAN_ROLE_EDITOR_SELECT, timeout=10)
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "选择按钮点击后未落地「AI形象」页 [OCR·顶栏区]")
        assert self.userA.text_exists("完成", timeout=8) is not None, (
            "AI 形象页「完成」按钮缺失 [OCR]")  # ⛔ 仅存在性断言，绝不点击
        # DIY 页
        self.userA.click_image(SWAN_ROLE_IMAGES_DIY_BTN, timeout=10)
        assert self.userA.find_ai_topbar_text("DIY形象", timeout=10) is not None, (
            "DIY形象按钮点击后未落地「DIY形象」页 [OCR·顶栏区]")
        assert self.userA.text_exists("上传照片", timeout=8) is not None, (
            "DIY 页「上传照片」素材区缺失 [OCR]")
        assert self.userA.text_exists("选择风格", timeout=8) is not None, (
            "DIY 页「选择风格」素材区缺失 [OCR]")

        # 逐级返回：DIY → AI 形象 → 编辑器 → AI 首页
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("AI形象", timeout=10) is not None, (
            "DIY 页返回后未回到「AI形象」页 [OCR·顶栏区]")
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "AI 形象页返回后未回到编辑器「自定义设置」[OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
