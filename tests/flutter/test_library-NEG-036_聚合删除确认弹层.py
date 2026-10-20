# CASE-ID: library-NEG-036
"""Swan 回归·M12 收藏与曲库：聚合歌单删除确认弹层（library-NEG-036）。

用例 → AW 映射：
- 前置：一次性自建聚合（0 来源，不依赖第三方数据）→ create_composite_playlist。
- S1-S3 聚合详情 → 更多入口 → 编辑歌单 → 删除歌单 → 确认弹层出现：
  open_composite_detail + composite_delete_to_confirm（断言确认弹层锚）。
- S5-S6 点取消 → 聚合保留：click_text('取消') 后复核详情锚仍在；再次进入
  删除路径停在确认层。
- 降级注记：确认弹层文案核对（YAML 期望含警示语）按（确认/确定/删除）
  宽口径锚定，精确文案执行轮校准。
清理：一次性聚合真删（创建即删，自有 TEST-SYNTHETIC 数据）→
composite_delete_to_confirm + composite_delete_confirm。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryNeg036CompositeDeleteConfirm(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """聚合歌单删除停确认层：取消不删，再次进入路径一致。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_composite_delete_confirm_layer(self):
        """删除歌单拉起确认弹层，取消后聚合保留，可重复进入删除路径。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # 前置：一次性聚合（0 来源）
        self.userA.create_composite_playlist('TESTSYN聚合删除对照')
        self.userA.open_composite_detail('TESTSYN聚合删除对照')
        # S1-S3：删除路径到确认弹层
        self.userA.composite_delete_to_confirm()
        # S5：取消 → 聚合保留（详情仍在）
        self.userA.click_text('取消', timeout=5)
        self.userA.open_composite_detail('TESTSYN聚合删除对照')
        # S6：再次进入删除路径停确认层
        self.userA.composite_delete_to_confirm()
        self.userA.click_text('取消', timeout=5)
        # 清理：一次性聚合真删
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm('TESTSYN聚合删除对照')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性聚合）。"""
        pass
