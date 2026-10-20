# CASE-ID: launch-POS-010
"""Swan 回归·M01 启动与隐私：隐私弹层两条协议链接外跳与回跳（launch-POS-010）。

用例 → AW 映射：
- 冷启动弹出隐私弹层 → 夹具冷启动 + privacy_dialog_visible() 探测
- 点「用户协议」外跳浏览器 → [OCR] 点击 + 弹层不在屏断言（已离开弹层）
- 返回回弹层 → press_back() + privacy_dialog_visible() 断言
- 点「隐私政策」外跳 → 同链路重复一轮
状态条件：需全新安装未同意态窗口（privacyRequired）；135 常态已同意
无弹层，不可见即 skip。链接 OCR 与登录页底部协议文案存在同屏歧义风险
（B 类登记 template_needs：链接 [图] 模板 + 浏览器协议页锚点 [图]）。
清理（YAML cleanup）：teardown 点击「同意」恢复同意态，供后续用例衔接。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchPos010ProtocolLinks(SwanRP01Mixin, BaseTest):
    """隐私弹层两条协议链接外跳与回跳（launch-POS-010）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_protocol_links_jump_and_return(self):
        """点协议链接外跳浏览器，返回后弹层应原样重现（两链接各一轮）。"""
        if not self.userA.privacy_dialog_visible(timeout=3):
            pytest.skip("隐私弹层不可见（账号已同意态）——需全新安装未同意窗口")
        # 链接①：用户协议
        self.userA.click_text("用户协议", timeout=10)
        assert self.userA.find_text_by_ocr("用户隐私协议概要", timeout=3) is None, (
            "点击「用户协议」后弹层仍在屏（未外跳）")
        self.userA.press_back()
        assert self.userA.privacy_dialog_visible(timeout=5), (
            "浏览器返回后隐私弹层未重现")
        # 链接②：隐私政策
        self.userA.click_text("隐私政策", timeout=10)
        assert self.userA.find_text_by_ocr("用户隐私协议概要", timeout=3) is None, (
            "点击「隐私政策」后弹层仍在屏（未外跳）")
        self.userA.press_back()
        assert self.userA.privacy_dialog_visible(timeout=5), (
            "浏览器返回后隐私弹层未重现")

    def teardown(self) -> None:
        """用例私有清理（YAML cleanup）：点击「同意」恢复同意态。"""
        if self.userA.privacy_dialog_visible(timeout=2):
            self.userA.accept_privacy_dialog()
