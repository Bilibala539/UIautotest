# CASE-ID: radio-POS-013
"""Swan 回归·电台：80er 页全量列表渲染与无分页模型（radio-POS-013，坑 8 正向面）。

步骤 -> AW 映射（/radio/80s FmHarmonyRadioPage harmony80 通道；
getHarmonyFmList 一次性全量，无分页无分类）：
- 步骤1 经首页 80er 区块进入 -> go_top_tab('电台') + tap_card_by_texts
  （l10n fmRadio80erTitle 中文未核准候选兜底）+ ocr_page_texts 计数
  （全量列表渲染项观察）；
- 步骤2 首项 hero 大图装饰 -> 形态为图像级断言，合成模板未入库，
  登记 package_report.template_needs（本条 OCR 侧以列表渲染完整兜底，
  视觉精比对留图像兜底轮）；
- 步骤3 触底观察无加载更多语义 -> swipe_up 触底后断言无「加载中」
  文案（Harmony 无分页模型）且列表仍渲染。

清理：纯查询，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadio80sFullList(BaseTest):
    """radio-POS-013：80er 页全量列表，触底无分页语义。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_80s_full_list(self):
        """80er 页列表全量渲染，触底无加载更多。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1：进 80er 页，全量列表渲染
        self.userA.tap_card_by_texts("80后", "80后电台", "80er", "80")
        texts = self.userA.ocr_page_texts()
        assert len(texts) >= 5, f"80er 页列表渲染项过少: {len(texts)}"
        # 步骤3：触底无加载更多语义（步骤2 hero 形态留图像兜底轮）
        for _ in range(3):
            self.userA.swipe_up()
        assert self.userA.find_text_by_ocr("加载中",
                                           timeout=2) is None, \
            "80er 页触底出现加载中文案（不应有分页模型）"
        texts_after = self.userA.ocr_page_texts()
        assert len(texts_after) >= 3, "触底后列表渲染异常"

    def teardown(self) -> None:
        """纯查询无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
