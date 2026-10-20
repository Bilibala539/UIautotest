# CASE-ID: search-POS-014
"""Swan 回归·搜索：返回键状态机（结果态→历史态→退出）(search-POS-014)。

步骤→AW 映射：
- 进搜索输入页 → open_search_input_page（推荐 Tab 搜索条；YAML 原文为
  音乐 Tab 入口，verify R2 拍板搜索条已回归推荐 Tab，按现状口径转换）
- 搜索 'ocean' → submit_search_keyword('ocean')（结果顶 Tab 行断言在 mixin）
- 结果态按返回 → press_back + text_exists('搜索歌曲或艺术家等')
  （关键词清空回历史态、不退出搜索页：输入页 hint 恢复为锚）
- 历史态再按返回 → press_back + assert_on_home()（退出搜索页回首页）

cleanup：无用例私有清理（冷启动模型，teardown body 一律 pass）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestBackKeyStateMachine(SwanRP03Mixin, BaseTest):
    """返回键两级状态机：结果态回历史态不退出，历史态退出回首页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_back_key_state_machine(self):
        """结果态 back → 历史态（hint 恢复）；再 back → 首页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        self.userA.submit_search_keyword('ocean')

        self.userA.press_back()
        self.userA.text_exists('搜索歌曲或艺术家等', timeout=5)

        self.userA.press_back()
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在首页
