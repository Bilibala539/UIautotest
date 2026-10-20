# CASE-ID: profile-POS-029
"""Swan 回归·M13 个人中心：毛玻璃顶栏标题渐显双向（profile-POS-029）。

用例 → AW 映射（B 级：毛玻璃渲染细节 OCR 不可辨 → 模板需求已登记）：
- 页顶：顶栏无标题「我的」（渐隐态）→ me_top_bar_text 反向断言（顶部 12% 区域 OCR）
- 滚动到列表中部 → 标题渐显
- 滚回页顶 → 标题复隐（双向）
- 毛玻璃材质/透明度视觉面 → 模板需求登记
清理（G3/G4）：滚动只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos029TitleBarGlassReveal(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_title_bar_glass_reveal(self) -> None:
        self.userA.open_me_page()
        # 页顶：标题渐隐
        assert not self.userA.me_top_bar_text("我的", timeout=2), \
            "页顶时顶栏不应出现标题「我的」"
        # 滚动：标题渐显
        self.userA.me_row_scroll_until("音质设置")
        assert self.userA.me_top_bar_text("我的", timeout=2), \
            "滚动后顶栏标题「我的」未渐显"
        # 回顶：标题复隐
        for _ in range(4):
            self.userA.swipe_down(400)
        assert not self.userA.me_top_bar_text("我的", timeout=2), \
            "回顶后顶栏标题未复隐"

    def teardown(self) -> None:
        pass
