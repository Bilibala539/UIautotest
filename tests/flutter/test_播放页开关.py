"""Swan Flutter 播放页开关只读断言（原 test_swan_readonly_pages.py，2026-10-12 拆分）。

前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：播放暂停/音量/上下首控制键。
断言优先级：图片（image_exists）> key（wait_accessibility）> OCR。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_PLAY_PAUSE_BTN,
)
from utils.aw.business.swan import SwanBusiness
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestSwanPlayerOpenClose(SwanLoginRegressionMixin, BaseTest):
    """播放页开关只读断言。"""

    def setup(self) -> None:
        """pytest 生命周期钩子（模板要求显式声明；逻辑由 mixin 提供）。"""
        super().setup()

    def test_player_open_close(self):
        """播放页开关：点底部播放条进全屏播放页 → 断言后点收起按钮回首页。

        播放/暂停等控制键仅做存在性断言，⛔ 不点。
        """
        self._ensure_logged_in_on_home()
        self.aw.click_accessibility(SwanBusiness.KEY_BOTTOM_PLAYER)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_FULL_PLAYER_PAGE, timeout=15
        ), "未进入全屏播放页（full_player_page 未出现）"
        # 控制类入口仅存在性断言（key + 图片双校验），不下发点击
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_PLAYER_DISMISS_BUTTON
        ), "播放页缺少收起按钮"
        assert self.aw.accessibility_exists(
            SwanBusiness.KEY_PLAYER_PLAY_PAUSE_BUTTON
        ), "播放页缺少播放/暂停按钮"
        self.aw.image_exists(SWAN_PLAYER_DISMISS_BTN, timeout=10)
        self.aw.image_exists(SWAN_PLAYER_PLAY_PAUSE_BTN, timeout=10)

        self.aw.click_accessibility(SwanBusiness.KEY_PLAYER_DISMISS_BUTTON)
        assert self.aw.wait_accessibility(
            SwanBusiness.KEY_TAB_ME, timeout=15
        ), "收起播放页后未回到首页"
        self._assert_home_shell_image()
        self._probe_bottom_player_bar()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()