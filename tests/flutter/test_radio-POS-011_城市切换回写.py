# CASE-ID: radio-POS-011
"""Swan 回归·电台：城市选择切换回写与列表重置主路径（radio-POS-011）。

步骤 -> AW 映射（applyCitySelection 回写 Provider reset；cityCode 必传）：
- 步骤1 记录全国态列表基线后进城市选择页 -> ocr_page_texts 基线 +
  tap_card_by_texts('选择城市'/'切换城市'/'城市')；
- 步骤2 选择另一城市 X（TEST-SYNTHETIC 语义：取列表首个可用城市）->
  tap_first_list_item('选择城市'/'热门城市' 等框架词排除) 点击城市行；
- 步骤3 断言列表按城市 X 重载 -> 回全国页后 ocr_page_texts 内容集
  与基线 diff（reset 渲染目标城市电台，无混排由 Provider 契约承担）。

清理：会话内切回默认（重进城市页点「全国」兜底国家台语义），
teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioCitySwitch(BaseTest):
    """radio-POS-011：选城市回写后列表重置，收尾切回全国。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_city_switch_write_back(self):
        """选城市 -> 回写 reset -> 列表重载，收尾恢复默认。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 步骤1：全国态列表基线
        base_texts = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        # 进城市选择页
        self.userA.tap_card_by_texts("选择城市", "切换城市", "城市")
        self.userA.assert_any_of_texts("搜索城市", "选择城市", "热门城市",
                                       timeout=8)
        # 步骤2：取列表首个可用城市选中（args.cityCode 传递）
        self.userA.tap_first_list_item("选择城市", "热门城市")
        # 步骤3：回全国页，列表按城市重载（与基线 diff）
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        city_texts = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        assert city_texts != base_texts, "选城市后列表未重置"
        # 收尾：重进城市页切回「全国」（kFmNationalCityCode='000' 兜底语义）
        self.userA.tap_card_by_texts("选择城市", "切换城市", "城市")
        self.userA.click_any_text("全国", "全国电台", timeout=6)

    def teardown(self) -> None:
        """会话内已切回默认城市（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
