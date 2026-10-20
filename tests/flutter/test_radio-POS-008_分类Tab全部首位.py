# CASE-ID: radio-POS-008
"""Swan 回归·电台：全国台分类 Tab「全部」首位与跨分类列表（radio-POS-008）。

步骤 -> AW 映射（FmCountryRadioProvider._buildTypesWithAll 补首位
typeCode=''；坑 2 正向面：空串不传，选全部返回全部分类电台）：
- 步骤0 前置进全国电台页 -> go_top_tab('电台') + tap_card_by_texts
  （区块标题候选，中文未核准）；
- 步骤1 断言分类 Tab 渲染且首位「全部」 -> assert_any_of_texts('全部')
  （初始化串行链 20s 兜底由 find timeout 承担）；
- 步骤2 选中「全部」 -> click_any_text('全部')；
- 步骤3 断言列表跨分类覆盖 -> ocr_page_texts 渲染项计数
  （列表非空且完整渲染=未误限的可观察面；服务端跨分类覆盖契约
  OCR 侧不可枚举，登记 template_needs 后按渲染计数兜底）。

清理：纯查询，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioAllTypeFirstTab(BaseTest):
    """radio-POS-008：分类 Tab「全部」首位，选全部列表跨分类渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_all_type_first_tab(self):
        """「全部」页签在位可选中，列表渲染完整。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 前置：全国电台页
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 步骤1：分类 Tab 渲染且「全部」在位
        self.userA.assert_any_of_texts("全部", timeout=10)
        # 步骤2：选中「全部」（typeCode 空串不传契约）
        self.userA.click_any_text("全部")
        # 步骤3：列表渲染完整（跨分类覆盖未误限）
        texts = self.userA.ocr_page_texts()
        assert len(texts) >= 6, f"选全部后电台列表渲染项过少: {len(texts)}"

    def teardown(self) -> None:
        """纯查询无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
