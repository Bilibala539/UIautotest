# CASE-ID: nav-NEG-018
"""Swan 回归·M03 主框架导航：非白名单页收起播放条（nav-NEG-018）。

用例 → AW 映射：
- 音箱播放会话 → preset_playing("speaker")；收起全屏播放页 → 收起按钮
  探测链（SWAN_PLAYER_DISMISS_BTN/_LIGHT/_DARK，run4c 三模板口径，命中
  任一即点击）
- 我喜欢页（白名单）播放条在屏 → assert_mini_player_bar_text()
- 切我的页 → go_bottom_tab("我的") → 进音质设置（[图]
  SWAN_ME_SOUND_QUALITY_ROW，非白名单路由入口；设置类路由为 YAML 非
  白名单语义的代理入口）→ [图] SWAN_SOUND_QUALITY_DONE_BUTTON 页锚点
- 无播放条 → [图] SWAN_BOTTOM_PLAYER_BAR 不可见断言（会话态模板内容
  偏离判据偏弱，template_needs 登记会话态模板）
- 返回我的页播放条仍在 → press_back() + assert_mini_player_bar_text()
清理：无（下条用例冷启动自然接管播放会话）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_BOTTOM_PLAYER_BAR,
    SWAN_ME_SOUND_QUALITY_ROW,
    SWAN_PLAYER_DISMISS_BTN,
    SWAN_PLAYER_DISMISS_DARK,
    SWAN_PLAYER_DISMISS_LIGHT,
    SWAN_SOUND_QUALITY_DONE_BUTTON,
)
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavNeg018BarHiddenOffWhitelist(SwanRP01Mixin, BaseTest):
    """非白名单页收起播放条（nav-NEG-018）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_bar_hidden_on_non_whitelist_page(self):
        """白名单页播放条在屏，进非白名单设置页应收起，返回恢复。"""
        self.userA.preset_playing("speaker")
        for template in (SWAN_PLAYER_DISMISS_BTN, SWAN_PLAYER_DISMISS_LIGHT,
                         SWAN_PLAYER_DISMISS_DARK):
            if self.userA.find_image(template, timeout=1) is not None:
                self.userA.click_image(template, timeout=5)
                break
        self.userA.assert_mini_player_bar_text()
        self.userA.go_bottom_tab("我的")
        self.userA.click_image(SWAN_ME_SOUND_QUALITY_ROW, timeout=10)
        self.userA.image_exists(SWAN_SOUND_QUALITY_DONE_BUTTON, timeout=10)
        assert self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is None, (
            "非白名单设置页仍渲染迷你播放条（白名单包裹未生效）")
        self.userA.press_back()
        self.userA.assert_mini_player_bar_text()

    def teardown(self) -> None:
        """无用例私有清理（播放会话由下条用例冷启动自然接管）。"""
        pass
