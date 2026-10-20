# CASE-ID: radio-POS-002
"""Swan 回归·电台：全国/80er/90s 三详情页经首页三区块入口可达（radio-POS-002）。

步骤 -> AW 映射（首页 HomeRadioPage 三区块，terraceType 0/6/5，路由
/radio/country、/radio/80s、/radio/90s；radio 页族 0 testId）：
- 步骤1 首页电台 Tab 点击全国区块入口 -> go_top_tab('电台') +
  tap_card_by_texts('全国电台'/'国家台'/'全国') OCR 定位区块标题点击，
  到位断言城市入口文案；
- 步骤2 返回后点击 80er 区块入口 -> press_back + tap_card_by_texts
  （l10n fmRadio80erTitle 中文未核准，候选兜底），到位断言页签文案；
- 步骤3 返回后点击 90s 区块入口 -> press_back + tap_card_by_texts
  （l10n platformRadio90s 候选兜底），到位断言页签文案。

清理：只读冒烟，三详情页均为浏览态，teardown 按 pass（冷启动由框架承担）。
区块标题/详情页锚点中文串未核准 -> package_report.template_needs 登记。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioThreeDetailPages(BaseTest):
    """radio-POS-002：三区块入口逐一进详情页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_three_detail_pages(self):
        """全国/80er/90s 三详情页逐一可达。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 区块1：全国（terraceType 0 -> /radio/country）
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        self.userA.press_back()
        # 区块2：80er（terraceType 6 -> /radio/80s）
        self.userA.tap_card_by_texts("80后", "80后电台", "80er", "80")
        self.userA.assert_any_of_texts("全部", "80", timeout=8)
        self.userA.press_back()
        # 区块3：90s（terraceType 5 -> /radio/90s）
        self.userA.tap_card_by_texts("90后", "90后电台", "90er", "90")
        self.userA.assert_any_of_texts("全部", "90", timeout=8)

    def teardown(self) -> None:
        """只读冒烟无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
