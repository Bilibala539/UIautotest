# CASE-ID: profile-POS-011
"""Swan 回归·M13 个人中心：本地音乐页壳进入（profile-POS-011）。

用例 → AW 映射（B 级：本地音乐行 2026-09-08 dump 未渲染，坑19 漂移；页锚未探索）：
- 行渲染时进入 → assert_page_not_blank 兜底 → back 返回
- 行未渲染 → pytest.skip 如实上报环境漂移
- 页内容锚未探索 → 模板需求已登记（本地音乐页锚）
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos011LocalMusicShell(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_local_music_page_shell(self) -> None:
        self.userA.open_me_page()
        if not self.userA.me_row_scroll_until("本地音乐"):
            pytest.skip("本地音乐行未渲染（坑19 漂移，以实测为准）")
        self.userA.click_text("本地音乐")
        self.userA.assert_page_not_blank()
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
