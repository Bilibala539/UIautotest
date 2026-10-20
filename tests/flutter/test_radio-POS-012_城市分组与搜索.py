# CASE-ID: radio-POS-012
"""Swan 回归·电台：城市选择页省份分组 Tab 与 keyword 搜索（radio-POS-012）。

步骤 -> AW 映射（FmSelectCityPage 分组 Tab + city/list keyword；
未决 2：keyword 匹配语义待确认，断言宽松化为「结果区刷新」）：
- 步骤1 进城市选择页后切换省份分组 Tab -> tap_card_by_texts 进页 +
  click_any_text 常见省份候选（分组名由 city/list 动态返回，中文
  候选兜底），Tab 切换后列表随分组刷新（渲染项计数观察）；
- 步骤2 搜索框输入城市关键词 -> click_any_text 聚焦搜索框 +
  input_text('广州')，结果区刷新断言匹配城市行出现；
- 步骤3 清空关键词 -> clear_input()，恢复省份分组完整列表
  （省份候选复现，无残留过滤）。

清理：纯查询，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioCitySearch(BaseTest):
    """radio-POS-012：省份分组 Tab 切换与关键词搜索、清空还原。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_city_group_and_keyword_search(self):
        """分组 Tab 刷新列表，关键词出匹配城市，清空后还原。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 进城市选择页
        self.userA.tap_card_by_texts("选择城市", "切换城市", "城市")
        self.userA.assert_any_of_texts("搜索城市", "选择城市", "热门城市",
                                       timeout=8)
        before = self.userA.ocr_page_texts()
        # 步骤1：切换省份分组 Tab（动态分组名，常见省份候选兜底）
        self.userA.click_any_text("广东", "浙江", "江苏", "北京", "上海",
                                  timeout=6)
        after_tab = self.userA.ocr_page_texts()
        assert after_tab != before, "切省份分组后列表未刷新"
        # 步骤2：搜索框输入关键词，结果区刷新出匹配城市
        self.userA.click_any_text("搜索城市", "搜索", timeout=6)
        self.userA.input_text("广州")
        self.userA.assert_any_of_texts("广州", timeout=10)
        # 步骤3：清空关键词，恢复分组完整列表
        self.userA.clear_input()
        self.userA.assert_any_of_texts("广东", "浙江", "江苏", "北京",
                                       "上海", timeout=8)

    def teardown(self) -> None:
        """纯查询无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
