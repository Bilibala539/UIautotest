# CASE-ID: library-POS-021
"""Swan 回归·M12 收藏与曲库：聚合歌单改名（library-POS-021）。

用例 → AW 映射：
- 前置：一次性自建聚合（0 来源）——YAML 前置为既有聚合歌单；0 来源聚合
  改名路径与带来源一致，风险注记见 report.notes。
- S1-S2 聚合详情 → 更多入口 → 编辑歌单：open_composite_detail +
  open_composite_edit_dialog。
- S3-S5 改名：click_text('改名') → clear_input → input_text(新名) → 保存 →
  新名可见（composite_rename 内断言）。
- S6 列表同步：press_back → open_composite_segment → text_exists(新名)。
- S7 清理改回：open_composite_detail(新名) → composite_rename(原名)。
清理：一次性聚合真删 → composite_delete_to_confirm + composite_delete_confirm。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos021CompositeRename(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """聚合歌单改名：编辑弹层改名生效，详情与列表同步新名，可改回删除。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_composite_rename(self):
        """聚合改名闭环：新名回显、列表同步、改回还原并真删。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # 前置：一次性聚合（0 来源）
        self.userA.create_composite_playlist('TESTSYN聚合改名R0')
        # S1-S5：详情 → 编辑弹层 → 改名保存
        self.userA.open_composite_detail('TESTSYN聚合改名R0')
        self.userA.composite_rename('TESTSYN聚合改名R2新名')
        # S6：列表同步
        self.userA.press_back()
        self.userA.open_composite_segment()
        self.userA.text_exists('TESTSYN聚合改名R2新名', timeout=10)
        # S7：清理改回
        self.userA.open_composite_detail('TESTSYN聚合改名R2新名')
        self.userA.composite_rename('TESTSYN聚合改名R0')
        # 清理：真删
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm('TESTSYN聚合改名R0')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性聚合）。"""
        pass
