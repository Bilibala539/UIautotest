# CASE-ID: search-POS-005
"""Swan 回归·搜索：电台 Tab 搜索入口进搜索输入页(search-POS-005)。

步骤→AW 映射（B 级：电台 Tab 页面本体知识库标记未探索——授权门禁拦截
未进入，页内搜索入口以既有模板 SWAN_HOME_RADIO_SEARCH_BAR 探测）：
- 切电台 Tab → go_top_tab('电台')（顶 Tab 选中态锚断言）
- 点电台 Tab 搜索条进输入页 → open_search_input_page(
  bar_image=SWAN_HOME_RADIO_SEARCH_BAR)（mixin 内含授权通知弹层处置 +
  输入页 hint '搜索歌曲或艺术家等' 到位断言；若门禁拦截入口，探测失败
  即真实现象，不做伪通过）

cleanup：无用例私有清理（结束态为搜索输入页，随冷启动复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_RADIO_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestRadioTabSearchEntry(SwanRP03Mixin, BaseTest):
    """电台 Tab 搜索条进入搜索输入页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_radio_tab_search_entry(self):
        """电台 Tab → 搜索条 → 输入页 hint 到位。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('电台')
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_RADIO_SEARCH_BAR)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索输入页
