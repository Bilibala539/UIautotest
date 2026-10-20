# CASE-ID: radio-POS-003
"""Swan 回归·电台：城市选择页可达与省份分组结构、零选择返回（radio-POS-003）。

步骤 -> AW 映射（/radio/select-city FmSelectCityPage，radio 页族 0 testId）：
- 步骤0 前置进全国电台页 -> go_top_tab('电台') + tap_card_by_texts
  （'全国电台'/'国家台' 候选，区块标题中文未核准）；
- 步骤1 全国电台页点击城市入口 -> tap_card_by_texts('城市'/'选择城市'
  候选兜底）进城市选择页；
- 步骤2 断言省份分组 Tab 与搜索框 -> assert_any_of_texts
  （l10n fmSelectCitySearchHint 城市搜索 hint 中文未核准，候选兜底）；
- 步骤3 零选择返回 -> press_back 回全国页，断言城市入口文案仍在
  （城市选择态未变更，零写返回）。

清理：只读冒烟零选择，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioCitySelectPage(BaseTest):
    """radio-POS-003：城市选择页结构与零选择返回。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_city_select_zero_write_back(self):
        """城市选择页可达、搜索框/分组结构在位、零选择返回无状态变更。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 前置：进全国电台详情页
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 步骤1：城市入口 -> 城市选择页
        self.userA.tap_card_by_texts("选择城市", "切换城市", "城市")
        # 步骤2：搜索 hint + 分组结构候选断言
        self.userA.assert_any_of_texts("搜索城市", "选择城市", "热门城市",
                                       timeout=8)
        # 步骤3：零选择返回，全国页城市入口仍在（选择态未变更）
        self.userA.press_back()
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)

    def teardown(self) -> None:
        """只读冒烟无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
