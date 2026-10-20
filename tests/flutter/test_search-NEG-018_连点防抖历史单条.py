# CASE-ID: search-NEG-018
"""Swan 回归·搜索：同词连点提交防抖——历史恰 1 条(search-NEG-018,部分转换)。

步骤→AW 映射（历史初态经 UI 自造可控，无需人工预置）：
- 前置可控初态：进输入页，历史区有'删除'入口则删除模式清空
- 输入合成词后连续提交 3 次 → click hint + input_text('synthkw-dbl')
  + click_image(SWAN_SEARCH_SUBMIT) 连点 ×3（SearchPage 顶栏跨输入态/
  结果态持续在场，连点可落）
- 断言历史该词恰 1 条 → press_back + count_texts_containing(
  'synthkw-dbl') == 1（去重生效，无重复写入）
- ANR 守门 → assert_no_anr_dialog()

⚠️ 部分转换注记：「搜索请求计数 ≤1」子断言需网络请求观测——框架无抓包/
请求计数通道（TCBATCH1-ADD1 点名能力缺口），OCR 承载面=历史恰 1 条+
无 ANR+页面正常；缺口锚（search_page.dart:203-220 提交链无显式防抖，
破坏点候选）已记录，执行轮如需请求级证据须先补抓包通道。
cleanup：teardown 清空自建历史（用例私有清理）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_HOME_MUSIC_SEARCH_BAR,
    SWAN_SEARCH_SUBMIT,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestDoubleSubmitDebounce(SwanRP03Mixin, BaseTest):
    """同词 1 秒内连点提交 3 次：历史去重恰 1 条，无 ANR。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_double_submit_debounce_single_history(self):
        """连点提交 3 次 → 历史该词恰 1 条 → 无 ANR。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')
        if self.userA.find_text_by_ocr('删除', timeout=2) is not None:
            self.userA.enter_search_history_delete_mode()
            self.userA.click_text('清空', timeout=5)
            self.userA.click_text('清空', timeout=5)

        self.userA.click_text('搜索歌曲或艺术家等', timeout=10)
        self.userA.input_text('synthkw-dbl')
        for _ in range(3):
            self.userA.click_image(SWAN_SEARCH_SUBMIT, timeout=5)

        self.userA.press_back()
        assert self.userA.count_texts_containing('synthkw-dbl') == 1, (
            "连点提交后历史词条数不等于 1（重复写入，去重失效）")
        self.userA.assert_no_anr_dialog()

    def teardown(self) -> None:
        """用例私有清理：清空自建历史（守卫后删除模式清空）。"""
        if self.userA.find_text_by_ocr('删除', timeout=2) is not None:
            self.userA.enter_search_history_delete_mode()
            self.userA.click_text('清空', timeout=5)
            self.userA.click_text('清空', timeout=5)
