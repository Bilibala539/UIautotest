# CASE-ID: nav-NEG-017
"""Swan 回归·M03 主框架导航：无播放会话不出现空迷你播放条（nav-NEG-017）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()
- 无播放会话前置探测 → 播放条 band [OCR] 非空即说明 rig 存在持久播放
  会话（relaunch 不清），本用例需无播放态窗口 → skip
- 打开歌单页但不起播 → open_playlist_detail("swan")（首页歌单卡→歌单页
  →SWAN 歌单行；SWAN 平台免授权，歌单行缺rows 由其内部断言暴露）
- 无播放条 → [图] SWAN_BOTTOM_PLAYER_BAR 不可见断言 → press_back() 回首页
（播放条 band 尾部多余留白为布局级像素测量，UI 自动化面不表达。）
清理：无（未起播，冷启动模型自然复位）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_BOTTOM_PLAYER_BAR


class TestNavNeg017NoEmptyBar(BaseTest):
    """无播放会话不出现空迷你播放条（nav-NEG-017）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_no_bar_without_playback(self):
        """未起播的歌单页不得出现迷你播放条。"""
        self.userA.ensure_logged_in_on_home()
        bar_items = self.userA.ocr_scan_page(region=(0, 1340, 720, 140))
        if any((i.get("text") or "").strip() for i in bar_items):
            pytest.skip("rig 存在持久播放会话（播放条 band 有文本）——本用例需无播放态窗口")
        self.userA.open_playlist_detail("swan")
        assert self.userA.find_image(SWAN_BOTTOM_PLAYER_BAR, timeout=2) is None, (
            "无播放会话却出现迷你播放条（空播放条/空会话被渲染）")
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
