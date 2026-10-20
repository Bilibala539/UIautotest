# CASE-ID: ai-POS-040
"""Swan 回归·AI 助手域：未授权平台开通入口存在性·不真跳授权流（ai-POS-040）。

步骤 → AW 映射：
1. 定位未授权平台卡 → open_ai_role_editor + click_text("更多AI平台") →
   首屏平台卡渲染断言（Qwen/DeepSeek/豆包/Kimi 头部行）
2. 断言开通入口存在（仅存在性）→ 开通入口为无文案控件（平台管理页
   OCR 仅平台名无按钮文本，wave5 实测）→ 探针：OCR 扫描 开通/去开通/
   未授权 类文本，未命中即条件 skip（template_needs 登记开通控件形态，
   图像模板补齐后以 probe_image 存在性断言转全自动）
3. 退出页面 → press_back ×2 零授权流拉起，编辑器/画廊锚回归

数据说明：⛔ 全程零点击（开通入口点击拉起原生授权流=禁区 3）；
本用例止步存在性确认。

cleanup：无（授权流零拉起；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiPlatformOpenEntry(SwanRM09Mixin, BaseTest):
    """未授权平台开通入口存在性（控件探针条件门，零点击零授权流）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_open_entry_exists(self):
        """平台卡渲染正确，开通入口存在性确认，零授权流拉起。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_role_editor()
        self.userA.click_text("更多AI平台", timeout=10)
        assert self.userA.find_ai_topbar_text("平台", timeout=10) is not None, (
            "平台管理页未达 [OCR·顶栏区]")

        # 步骤 1：未授权平台卡渲染（头部行）
        for platform in ("Qwen", "DeepSeek", "豆包", "Kimi"):
            assert self.userA.text_exists(platform, timeout=8) is not None, (
                f"平台卡「{platform}」未渲染 [OCR]")

        # 步骤 2：开通入口存在性探针（无文案控件，形态待标定）
        entry = None
        for kw in ("开通", "去开通", "未授权"):
            entry = self.userA.find_text_by_ocr(kw, timeout=2)
            if entry is not None:
                break
        if entry is None:
            self.userA.press_back()
            self.userA.press_back()
            self.userA.assert_ai_home_gallery()
            pytest.skip(
                "开通入口为无文案控件（平台行 OCR 仅平台名），控件图像模板"
                "未截取（template_needs: 平台卡开通入口）——已零点击返回")

        # 步骤 3：零授权流退出（⛔ 开通入口零点击）
        self.userA.press_back()
        assert self.userA.find_ai_topbar_text("自定义设置", timeout=10) is not None, (
            "平台管理页返回异常 [OCR·顶栏区]")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
