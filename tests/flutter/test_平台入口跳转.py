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

_platform = os.environ.get("PLATFORM", "web").strip().lower()
_has_phone = bool(os.environ.get("SWAN_PHONE", "").strip())

pytestmark = pytest.mark.skipif(
    _platform != "flutter" or not _has_phone,
    reason="Swan 用例需要 PLATFORM=flutter 和 SWAN_PHONE",
)

# (平台, 入口, expect_title)——expect_title 按 explorer 实测映射，勿跨平台复用
ENTRIES = [
    ("qq", "排行榜", "飙升榜"),
    ("netease", "排行榜", "排行榜"),
    ("netease", "歌单", "歌单"),
]


class TestPlatformEntryNavigation(SwanLoginRegressionMixin, BaseTest):
    """平台主页入口跳转（回归用例 38-40 深化）。"""

    @pytest.mark.parametrize("platform,entry,expect_title", ENTRIES)
    def test_open_platform_entry(self, platform, entry, expect_title):
        """平台主页入口跳转：入口 [OCR] 点击 + 落地页标题 [OCR] 断言。"""
        self._ensure_logged_in_on_home()
        self.aw.click_image(SWAN_TAB_PLATFORM, timeout=10)
        assert self.aw._platform_page_visible(), (
            "未到达平台页（网易云行两态 [图] 均未命中）")
        if self.aw.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                              timeout=3) is not None:
            pytest.skip(
                "账号未授权任何平台——平台内容用例需已授权态；授权域搁置中")
        self.user.open_platform_entry(platform, entry, expect_title)
        self.aw.press_back()  # 落地页 → 主页
        self.user.go_home()
