# CASE-ID: search-POS-015
"""Swan 回归·搜索：结果态点输入框回历史态并改词重搜(search-POS-015)。

步骤→AW 映射：
- 进搜索输入页 → open_search_input_page（推荐 Tab 搜索条；YAML 原文为
  音乐 Tab 入口，verify R2 拍板搜索条已回归推荐 Tab，按现状口径转换）
- 搜索 'ocean' → submit_search_keyword('ocean')
- 结果态点输入框 → click_text('ocean')（顶栏关键词 OCR 定位输入框，
  回历史态聚焦）
- 改词重搜 → submit_search_keyword('night', input_anchor='ocean')
  （mixin：先 clear_input 归零再输入，防光标追加拼词；结果顶 Tab 行断言）
- 断言历史含两词 → press_back + text_exists('ocean') + text_exists('night')

cleanup：无（搜索历史留两条测试词，随冷启动复位语义可接受）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestRekeywordFromResults(SwanRP03Mixin, BaseTest):
    """结果态点输入框改词重搜，历史同时记录新旧两词。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_rekeyword_from_results(self):
        """ocean 结果态 → 点输入框 → 改搜 night → 历史含 ocean/night。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        self.userA.submit_search_keyword('ocean')

        self.userA.click_text('ocean', timeout=5)
        self.userA.submit_search_keyword('night', input_anchor='ocean')

        self.userA.press_back()
        self.userA.text_exists('ocean', timeout=5)
        self.userA.text_exists('night', timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索历史态
