# CASE-ID: radio-NEG-006
"""Swan 回归·电台：80/90 电台无分页边界（radio-NEG-006，部分转换）。

步骤 -> AW 映射（可自动化面：步骤1/4 + 步骤2 的列表完整兜底；
radio 页族 0 testId）：
- 步骤1 进 80er 页断言无分页形态 -> tap_card_by_texts 进页 +
  ocr_page_texts 计数 + 触底后 text_not_exists/find 探测「加载中」
  不存在（一次性全量，勿按全国台分页模型断言）；
- 步骤2 hero 大图=index 0 装饰 -> 图像级形态模板未入库，登记
  package_report.template_needs，OCR 侧以列表渲染完整兜底（空首项
  越界防护为代码内契约，黑盒无注入窗口不单测）；
- 步骤3 空数据窗口观察 -> 空响应注入无手段，未纳入自动化
  （NOT-REPRODUCED 口径），见 package_report.notes；
- 步骤4 90s 页同构验证 -> 同构链路重复（harmony90 二分拉取形态一致）。

清理：只读断言，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioHarmonyNoPaging(BaseTest):
    """radio-NEG-006：80er/90s 页全量无分页，触底无加载中文案。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_harmony_no_paging(self):
        """80er/90s 页全量渲染、触底无分页语义。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1：80er 页无分页形态
        self.userA.tap_card_by_texts("80后", "80后电台", "80er", "80")
        texts = self.userA.ocr_page_texts()
        assert len(texts) >= 5, f"80er 页列表渲染项过少: {len(texts)}"
        for _ in range(3):
            self.userA.swipe_up()
        assert self.userA.find_text_by_ocr("加载中",
                                           timeout=2) is None, \
            "80er 页触底出现加载中文案（不应有分页模型）"
        # 步骤4：90s 页同构验证
        self.userA.press_back()
        self.userA.tap_card_by_texts("90后", "90后电台", "90er", "90")
        texts90 = self.userA.ocr_page_texts()
        assert len(texts90) >= 5, f"90s 页列表渲染项过少: {len(texts90)}"
        for _ in range(3):
            self.userA.swipe_up()
        assert self.userA.find_text_by_ocr("加载中",
                                           timeout=2) is None, \
            "90s 页触底出现加载中文案（不应有分页模型）"

    def teardown(self) -> None:
        """只读断言无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
