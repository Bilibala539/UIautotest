# CASE-ID: search-POS-003
"""Swan 回归·搜索：推荐页搜索入口进搜索输入页(search-POS-003)。

步骤→AW 映射：
- 进首页推荐 Tab → ensure_logged_in_on_home
- 点搜索条进输入页 → open_search_input_page(
  bar_image=SWAN_HOME_MUSIC_SEARCH_BAR, ocr_fallback='跨平台搜索音乐')
  （mixin 内含：条图优先/OCR 兜底 + 授权通知弹层处置 + 输入页 hint
  '搜索歌曲或艺术家等' [OCR] 到位断言）
- 返回首页 → press_back + assert_on_home

cleanup：无用例私有清理（冷启动模型，teardown body 一律 pass）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestRecommendSearchEntry(SwanRP03Mixin, BaseTest):
    """推荐 Tab 搜索条进入搜索输入页并可返回首页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_recommend_search_entry(self):
        """推荐 Tab 搜索条 → 输入页 hint 到位 → 返回断言首页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        self.userA.press_back()
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在首页
