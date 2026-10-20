# CASE-ID: radio-NEG-005
"""Swan 回归·电台：城市选择空态守卫与回写 reset（radio-NEG-005，部分转换）。

步骤 -> AW 映射（可自动化面：步骤1/2/4；radio 页族 0 testId）：
- 步骤0 前置进全国电台页 -> go_top_tab('电台') + tap_card_by_texts；
- 步骤1 进城市选择页观察分组基线 -> tap_card_by_texts('选择城市'
  候选）+ assert_any_of_texts 分组/搜索结构候选；
- 步骤2 keyword 乱串搜索（无结果）-> click_any_text 聚焦搜索框 +
  input_text('ZZQQXX')，空结果态页面存活（乱串回显 + 页面可继续
  交互；空结果文案中文未核准登记 template_needs）；
- 步骤3 city/list 空分组注入窗口无手段，未纳入自动化（NOT-REPRODUCED
  口径），见 package_report.notes；
- 步骤4 选中城市回写验证 -> clear_input 后 tap_first_list_item 选
  首个可用城市，回全国页断言列表 reset（与进页前基线 diff）。

清理：收尾切回「全国」（kFmNationalCityCode 兜底语义），teardown 按 pass。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioCityEmptyGuard(BaseTest):
    """radio-NEG-005：乱串空结果不崩、选中回写 reset 正确。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_city_empty_and_write_back(self):
        """乱串搜索空结果页面存活，选城市回写 reset 列表。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        base_texts = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        # 步骤1：城市选择页分组基线
        self.userA.tap_card_by_texts("选择城市", "切换城市", "城市")
        self.userA.assert_any_of_texts("搜索城市", "选择城市", "热门城市",
                                       timeout=8)
        # 步骤2：keyword 乱串（无结果），空结果态页面存活
        self.userA.click_any_text("搜索城市", "搜索", timeout=6)
        self.userA.input_text("ZZQQXX")
        self.userA.assert_any_of_texts("ZZQQXX", timeout=8)
        # 步骤4：清空后选中首个可用城市，回写 reset
        self.userA.clear_input()
        self.userA.tap_first_list_item("选择城市", "热门城市")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        city_texts = [t for t in self.userA.ocr_page_texts() if len(t) >= 4]
        assert city_texts != base_texts, "选城市后列表未 reset"
        # 收尾：切回「全国」默认城市
        self.userA.tap_card_by_texts("选择城市", "切换城市", "城市")
        self.userA.click_any_text("全国", "全国电台", timeout=6)

    def teardown(self) -> None:
        """会话内已切回默认城市（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
