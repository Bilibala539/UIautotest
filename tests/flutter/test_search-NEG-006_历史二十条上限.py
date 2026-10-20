# CASE-ID: search-NEG-006
"""Swan 回归·搜索：历史 20 条上限挤出边界(search-NEG-006,B 级)。

步骤→AW 映射（历史初态经 UI 自造可控，无需人工预置/stub）：
- 前置可控初态：进输入页，历史区有'删除'入口则经删除模式清空（UI 路径）
- 步骤1 依次搜索 20 个合成词 → submit_search_keyword(f'synthkw-h{i:02d}')
  + press_back（结果态→历史态）循环 20 次 → count_texts_containing(
  'synthkw-h') == 20（翻屏 OCR 去重计数）
- 步骤2 搜第 21 词 → h21 在场 + h01 被挤出 + 计数仍 20
- 步骤3 重搜历史中段词 h10（点历史芯片）→ 计数仍 20（去重不新增）+ h10 在场
- 步骤4 搜第 22 词 → h22 在场 + 此时最旧 h02 被挤出 + 计数仍 20

cleanup：teardown 清空自建历史（用例私有清理：历史态守卫'删除'后删除
模式清空确认）。
⚠️ B 级注记：条数统计走 OCR 翻屏去重口径，相邻芯片 OCR 并行可能欠计
（执行轮标定）；"置顶"以在场+计数守恒承载，未断言 y 序位置。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestHistoryTwentyCapEviction(SwanRP03Mixin, BaseTest):
    """历史 20 条硬上限：第 21/22 条挤出最旧、去重置顶、总数守恒。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def _clear_history_if_any(self) -> None:
        """用例前置：历史区存在'删除'入口则清空历史（可控初态）。"""
        if self.userA.find_text_by_ocr('删除', timeout=2) is not None:
            self.userA.enter_search_history_delete_mode()
            self.userA.click_text('清空', timeout=5)
            self.userA.click_text('清空', timeout=5)

    def test_history_twenty_cap_eviction(self):
        """20 次搜索建满历史 → 21/22 条挤出最旧 → 去重不新增。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        self._clear_history_if_any()

        for i in range(1, 21):
            self.userA.submit_search_keyword(f'synthkw-h{i:02d}')
            self.userA.press_back()
        assert self.userA.count_texts_containing('synthkw-h') == 20, (
            "20 次搜索后历史条数不等于 20（上限/去重契约存疑）")

        self.userA.submit_search_keyword('synthkw-h21')
        self.userA.press_back()
        self.userA.text_exists('synthkw-h21', timeout=5)
        self.userA.text_not_exists('synthkw-h01', timeout=5)
        assert self.userA.count_texts_containing('synthkw-h') == 20, (
            "第 21 条写入后总数应守恒 20（挤出最旧 h01）")

        self.userA.click_text('synthkw-h10', timeout=5)
        self.userA.press_back()
        assert self.userA.count_texts_containing('synthkw-h') == 20, (
            "重搜 h10 去重后不应新增条目")
        self.userA.text_exists('synthkw-h10', timeout=5)

        self.userA.submit_search_keyword('synthkw-h22')
        self.userA.press_back()
        self.userA.text_exists('synthkw-h22', timeout=5)
        self.userA.text_not_exists('synthkw-h02', timeout=5)
        assert self.userA.count_texts_containing('synthkw-h') == 20, (
            "第 22 条写入后总数应守恒 20（挤出此时最旧 h02）")

    def teardown(self) -> None:
        """用例私有清理：清空自建的 22 条历史（守卫后删除模式清空）。"""
        if self.userA.find_text_by_ocr('删除', timeout=2) is not None:
            self.userA.enter_search_history_delete_mode()
            self.userA.click_text('清空', timeout=5)
            self.userA.click_text('清空', timeout=5)
