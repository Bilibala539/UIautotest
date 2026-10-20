# CASE-ID: library-POS-031
"""Swan 回归·M12 收藏与曲库：聚合歌单详情页浏览（partial，library-POS-031）。

用例 → AW 映射：
- 前置：一次性自建聚合（0 来源）——YAML 前置为带来源既有聚合；浏览骨架
  一致，来源计数一致性断言降级（0 来源空态口径）。
- S1 进入详情：open_composite_detail（聚合段点行，详情锚断言）。
- S2 头部与添加歌单入口：assert_any_text(('添加歌单',))。
- S3 来源内容区：assert_any_text(('首歌', '暂无', '去添加'))（0 来源空态
  宽口径）。
- S4 退出无残留：press_back → assert_any_text(('创建', '收藏', '关联'))。
- 降级注记：boundCount 计数与实际来源数一致性（需带来源聚合+第三方数据）
  不转，登记 report.notes。
清理：一次性聚合真删 → composite_delete_to_confirm + composite_delete_confirm。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos031CompositeDetailBrowse(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """聚合详情浏览（partial）：头部与添加入口渲染，退出无残留。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_composite_detail_browse(self):
        """聚合详情可浏览：添加歌单入口与来源区渲染，退出回歌单页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # 前置：一次性聚合（0 来源）
        self.userA.create_composite_playlist('TESTSYN聚合详情浏览')
        # S1：进入详情
        self.userA.open_composite_detail('TESTSYN聚合详情浏览')
        # S2：添加歌单入口
        self.userA.assert_any_text(('添加歌单',), timeout=8)
        # S3：来源内容区（0 来源空态）
        self.userA.assert_any_text(('首歌', '暂无', '去添加'), timeout=8)
        # S4：退出无残留
        self.userA.press_back()
        self.userA.assert_any_text(('创建', '收藏', '关联'), timeout=8)
        # 清理：真删一次性聚合
        self.userA.open_composite_detail('TESTSYN聚合详情浏览')
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm('TESTSYN聚合详情浏览')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性聚合）。"""
        pass
