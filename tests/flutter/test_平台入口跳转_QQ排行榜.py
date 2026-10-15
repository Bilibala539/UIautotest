# CASE-ID: aw-平台入口跳转_QQ排行榜
# LINKED-CASE: REG-038,REG-039,REG-040
"""Swan 回归·域6：平台主页入口跳转（回归用例 38-40 深化）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域6）：
- 平台主页入口跳转 → open_platform_entry(platform, entry, expect_title)

⚠️ 状态条件用例：同 test_平台内容页进入（需已授权态，未授权自动 skip）。
expect_title 映射见 SwanBusiness._PLATFORM_ENTRY_TITLES（⚠️ 不可跨平台
复用：同名"排行榜"入口 QQ 落飙升榜详情、网易云落排行榜聚合页）。
清理：同 test_平台内容页进入。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
    SWAN_TAB_PLATFORM,
)
from utils.aw.business.swan_regression import SwanLoginRegressionMixin


class TestPlatformEntryNavigation(SwanLoginRegressionMixin, BaseTest):
    """平台主页入口跳转（回归用例 38-40 深化）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_open_platform_entry(self):
        """平台主页入口跳转：入口 [OCR] 点击 + 落地页标题 [OCR] 断言。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.click_image(SWAN_TAB_PLATFORM, timeout=10)
        assert self.userA._platform_page_visible(), (
            "未到达平台页（网易云行两态 [图] 均未命中）")
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                              timeout=3) is not None:
            pytest.skip(
                "账号未授权任何平台——平台内容用例需已授权态；授权域搁置中")
        self.userA.open_platform_entry('qq', '排行榜', '飙升榜')
        self.userA.press_back()  # 落地页 → 主页
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
