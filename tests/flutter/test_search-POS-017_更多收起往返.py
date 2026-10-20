# CASE-ID: search-POS-017
"""Swan 回归·搜索：分组'更多/收起'往返展开收起(search-POS-017)。

步骤→AW 映射：
- 搜索（结果分组数据就绪门槛）→ search(keyword, entry='home') +
  assert_search_results('单曲', platforms, allow_empty=False)
- 展开 → click_text('更多') + text_exists('收起')（按钮态切换 [OCR]）
- 收起 → click_text('收起') + text_exists('更多')（往返复原）

⚠️ 注记：①关键词/平台断言范围走环境变量（SWAN_SEARCH_KEYWORD /
SWAN_SEARCH_PLATFORMS，账号授权态相关，与既有搜索用例同口径），缺省
'piano'；②'更多'入口要求存在 >5 条分组（数据依赖现网/账号，数据不足时
click_text 失败即数据门槛未满足，如实失败）。
cleanup：无用例私有清理（冷启动模型）。
"""
from __future__ import annotations

import os

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestGroupExpandCollapseToggle(SwanRP03Mixin, BaseTest):
    """结果分组'更多/收起'往返切换。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_group_expand_collapse_toggle(self):
        """点'更多'出现'收起'，点'收起'复原'更多'。"""
        keyword = os.environ.get("SWAN_SEARCH_KEYWORD", "").strip() or "piano"
        platforms = [p.strip() for p in
                     os.environ.get("SWAN_SEARCH_PLATFORMS", "").split(",")
                     if p.strip()]

        self.userA.ensure_logged_in_on_home()
        self.userA.search(keyword, entry='home')
        self.userA.assert_search_results('单曲', platforms, allow_empty=False)

        self.userA.click_text('更多', timeout=5)
        self.userA.text_exists('收起', timeout=5)
        self.userA.click_text('收起', timeout=5)
        self.userA.text_exists('更多', timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索结果页（收起态）
