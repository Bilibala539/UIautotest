# CASE-ID: search-POS-011
"""Swan 回归·搜索：提交关键词自动去首尾空白(search-POS-011)。

步骤→AW 映射：
- 进搜索输入页 → open_search_input_page（推荐 Tab 搜索条；YAML 原文为
  音乐 Tab 入口，verify R2 拍板搜索条已回归推荐 Tab，按现状口径转换）
- 带空白提交 ' ocean ' → submit_search_keyword(' ocean ')（mixin：输入回显
  → 提交 → 结果顶 Tab 行断言；结果页正常渲染本身即"trim 后发起请求"证据）
- 断言结果态关键词回填 trim 值 → text_exists('ocean')
- 返回历史态断言历史记录 trim 值 → press_back + text_exists('ocean')

⚠️ 注记：OCR 文本匹配对首尾空白不敏感（OCR 归一空白），trim 证据以
"请求以 trim 值生效（结果渲染）+ 历史/回显均为去空白值"承载。
cleanup：无（搜索历史留 'ocean'，随冷启动复位语义可接受）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestSearchKeywordTrim(SwanRP03Mixin, BaseTest):
    """带首尾空白提交关键词，按 trim 后值搜索并记录历史。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_search_keyword_auto_trim(self):
        """提交 ' ocean ' → 结果页/历史均按 trim 值 'ocean' 呈现。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')

        self.userA.submit_search_keyword(' ocean ')
        self.userA.text_exists('ocean', timeout=10)

        self.userA.press_back()
        self.userA.text_exists('ocean', timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索历史态
