# CASE-ID: library-POS-022
"""Swan 回归·M12 收藏与曲库：聚合歌单删除约束到确认层（library-POS-022）。

用例 → AW 映射：
- 前置：一次性自建聚合（0 来源，替代 YAML 既有聚合前置，自有数据口径）。
- S1-S3 聚合详情 → 更多 → 编辑歌单 → 删除歌单：composite_delete_to_confirm
  （断言确认弹层出现，删除约束收口到确认层）。
- S4-S5 点取消：click_text('取消')，聚合保留。
- S6 复核仍存在：详情锚 + 聚合段列表名可见。
- 降级注记：确认弹层警示文案精确断言执行轮校准（宽口径确认锚）。
清理：一次性聚合真删（创建即删，自有数据）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PD_MORE_BTN
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos022CompositeDeleteConstraint(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """聚合删除约束到确认层：取消后聚合完整保留在详情与列表。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_composite_delete_constraint(self):
        """删除歌单停在确认层，取消后详情与列表均保留聚合。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # 前置：一次性聚合（0 来源）
        self.userA.create_composite_playlist('TESTSYN聚合删除约束')
        # S1-S3：删除路径到确认弹层
        self.userA.open_composite_detail('TESTSYN聚合删除约束')
        self.userA.composite_delete_to_confirm()
        # S4-S5：取消
        self.userA.click_text('取消', timeout=5)
        # S6：复核仍存在（详情锚 + 列表名）
        self.userA.image_exists(SWAN_PD_MORE_BTN, timeout=5)
        self.userA.press_back()
        self.userA.open_composite_segment()
        self.userA.text_exists('TESTSYN聚合删除约束', timeout=10)
        # 清理：真删一次性聚合
        self.userA.open_composite_detail('TESTSYN聚合删除约束')
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm('TESTSYN聚合删除约束')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性聚合）。"""
        pass
