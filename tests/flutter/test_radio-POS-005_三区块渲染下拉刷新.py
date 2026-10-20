# CASE-ID: radio-POS-005
"""Swan 回归·电台：首页电台 Tab 三区块渲染与下拉刷新（radio-POS-005）。

步骤 -> AW 映射（HomeRadioPage 全国=index 0-3 / 80er·90s=index 4-7，
HomeSectionHeader 结构兜底，radio 页族 0 testId）：
- 步骤1 进入首页电台 Tab 断言三区块标题 -> go_top_tab('电台') +
  assert_any_of_texts（区块标题 l10n 中文未核准，候选兜底）；
- 步骤2 断言各区块卡片渲染 -> swipe_up 下滑后 ocr_page_texts 计数
  （卡片标题+封面渲染产生多条文本项，渲染项计数兜底）；
- 步骤3 下拉刷新 -> swipe_down 重载后区块标题复现（LottieRefreshWrapper
  正向面；渲染代次保护防重复卡片由服务端契约承担，OCR 侧断刷新可用）。

清理：只读断言，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioHomeSections(BaseTest):
    """radio-POS-005：三区块渲染、卡片在位、下拉刷新可用。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_home_sections_render(self):
        """三区块标题齐备，内容卡片渲染，下拉刷新后复现。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1：三区块标题（候选兜底，见 template_needs）
        self.userA.assert_any_of_texts("全国电台", "国家台", "全国", timeout=8)
        self.userA.assert_any_of_texts("80后", "80er", "80", timeout=5)
        self.userA.assert_any_of_texts("90后", "90er", "90", timeout=5)
        # 步骤2：区块内卡片渲染（下滑后 OCR 文本项计数）
        self.userA.swipe_up()
        texts = self.userA.ocr_page_texts()
        assert len(texts) >= 6, f"电台 Tab 卡片区渲染文本项过少: {len(texts)}"
        # 步骤3：下拉刷新重载，区块标题复现
        self.userA.swipe_down()
        self.userA.assert_any_of_texts("全国电台", "国家台", "全国", timeout=8)

    def teardown(self) -> None:
        """只读断言无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
