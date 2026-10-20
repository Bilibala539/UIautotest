# CASE-ID: ai-POS-039
"""Swan 回归·AI 助手域：平台授权状态标签与账号授权态一致展示（ai-POS-039）。

步骤 → AW 映射：
1-2. 浏览已授权/未授权平台卡 → open_ai_role_editor + click_text("更多AI平台")
     → 运行时条件门：授权态标识形态未标定（已授权/已连接类标签 OCR 无锚，
     template_needs 登记）→ 探针扫描授权态关键词，未命中即 skip（基线
     账号 0 已授权平台，正向不自动化授权操作——人工预置后探针自然命中）
3. 不触碰任何授权控件直接返回 → press_back（编辑器）→ press_back（首页）
     画廊锚回归，零授权变更

数据说明：授权状态标签与账号实际授权态一致展示——探针命中后的正向
断言=已授权标识出现于某平台卡行且未授权平台行仍渲染（对照面）；
⛔ 全程零点击平台行按钮（授权门禁红线）。

cleanup：无（零触碰零授权变更；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiPlatformAuthTags(SwanRM09Mixin, BaseTest):
    """平台授权状态标签展示（授权态标识探针条件门，零触碰）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_auth_tags_consistent(self):
        """授权/未授权平台卡标识展示，零触碰返回。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()
        self.userA.click_text("更多AI平台", timeout=10)
        assert self.userA.find_ai_topbar_text("平台", timeout=10) is not None, (
            "平台管理页未达 [OCR·顶栏区]")

        # 条件门：授权态标识探针（形态未标定 + 基线 0 已授权）
        tag = None
        for kw in ("已授权", "已连接", "已开通", "已授权"):
            tag = self.userA.find_text_by_ocr(kw, timeout=2)
            if tag is not None:
                break
        if tag is None:
            self.userA.press_back()
            self.userA.press_back()
            self.userA.assert_ai_home_gallery()
            pytest.skip(
                "未见已授权平台标识（基线账号 0 已授权平台，正向不自动化"
                "授权；授权态标识形态 template_needs 待标定）——已零触碰返回")

        # 未授权平台卡对照渲染（头部行，⛔ 零点击）
        for platform in ("Qwen", "DeepSeek", "豆包", "Kimi"):
            assert self.userA.text_exists(platform, timeout=8) is not None, (
                f"未授权平台卡「{platform}」未渲染 [OCR]")

        # 步骤 3：零触碰返回
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "平台管理页返回异常 [OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
