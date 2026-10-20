# CASE-ID: library-POS-019
"""Swan 回归·M12 收藏与曲库：聚合歌单创建弹层链（partial，library-POS-019）。

用例 → AW 映射：
- S1-S3 创建弹窗 → 关联类型 → 命名保存：open_create_playlist_dialog +
  click_text('关联') + input_text + 保存 → 来源选择弹层自动拉起。
- S4 弹层结构：assert_any_text(('添加歌单', '完成'))（标题+完成按钮 OCR 宽口径）。
- 降级注记：S5-S7 候选歌单勾选/来源提交段不转——候选为第三方平台歌单
  （需已授权第三方数据，THIRD_PARTY_REAL 面）；本用例以 0 来源一次性聚合
  走完创建链，勾选段缺口在 report.template_needs/notes 登记。
- S8 聚合落列表：text_exists(<名>)。
清理：一次性聚合真删 → composite_delete_to_confirm + composite_delete_confirm。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos019CompositeCreateChain(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """聚合创建弹层链（partial）：关联类型创建+来源弹层结构+删除还原。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_composite_create_chain(self):
        """关联歌单创建：保存后来源弹层拉起，完成后聚合落列表并真删还原。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1-S2：创建弹窗 + 关联类型
        self.userA.open_create_playlist_dialog()
        self.userA.click_text('关联', timeout=5)
        # S3：命名保存 → 来源选择弹层自动拉起
        self.userA.input_text('TESTSYNTHETIC-M12-AGG-01')
        self.userA.click_text_candidates(('保存', '确定'))
        # S4：弹层结构（标题+完成按钮）
        self.userA.assert_any_text(('添加歌单', '完成'), timeout=10)
        # S5-S7 降级：来源勾选段不转（第三方候选数据依赖）
        self.userA.click_text('完成', timeout=5)
        # S8：聚合落列表
        self.userA.text_exists('TESTSYNTHETIC-M12-AGG-01', timeout=10)
        # 清理：真删一次性聚合
        self.userA.open_composite_detail('TESTSYNTHETIC-M12-AGG-01')
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm('TESTSYNTHETIC-M12-AGG-01')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性聚合）。"""
        pass
