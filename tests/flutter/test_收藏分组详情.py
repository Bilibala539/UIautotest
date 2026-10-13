"""Swan Flutter 收藏分组详情只读断言（原 test_swan_readonly_pages.py，2026-10-12 拆分）。

覆盖：我的页 → SWAN收藏 → 我的家庭分组详情。
前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：任何确认弹窗。
断言优先级：图片（image_exists）> key（wait_accessibility）> OCR。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_FAV_FAMILY_GROUP_ROW,
    SWAN_ME_FAVORITES_ROW,
)
from utils.aw.business.swan import SwanBusiness
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestSwanFavoritesGroupDetail(SwanLoginRegressionMixin, BaseTest):
    """收藏分组详情只读断言。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def test_favorites_group_detail(self):
        """收藏分组详情：我的页 → SWAN收藏 → 我的家庭 → OCR 断言 → 返回回首页。"""
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_TAB_ME)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_ME_PROFILE_ENTRY, timeout=15
        ), "未进入我的页"
        self.aw.click_image(SWAN_ME_FAVORITES_ROW)
        # 收藏页无 accessibility key，用图片行断言进入成功
        self.aw.image_exists(SWAN_FAV_FAMILY_GROUP_ROW, timeout=10)

        self.aw.click_image(SWAN_FAV_FAMILY_GROUP_ROW)
        # "我的家庭"详情页：无已知 key，按 OCR 断言（文案变体任一命中）
        self._assert_any_text(("播放全部", "首歌"), timeout=15)

        self.aw.press_back()  # 详情页 → SWAN收藏页
        self.aw.image_exists(SWAN_FAV_FAMILY_GROUP_ROW, timeout=10)
        self.aw.press_back()  # SWAN收藏页 → 我的页
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_ME_PROFILE_ENTRY, timeout=15
        ), "两次返回后未回到我的页"
        self.user.go_home()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()