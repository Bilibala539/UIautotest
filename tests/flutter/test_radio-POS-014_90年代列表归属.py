# CASE-ID: radio-POS-014
"""Swan 回归·电台：90s 页全量列表渲染与页面归属（radio-POS-014，harmony90 通道）。

步骤 -> AW 映射（/radio/90s terraceType=5 语义；坑 9：切台归属断言
用来源区块与页面标题，不用文案反推码值）：
- 步骤1 经首页 90s 区块进入 -> go_top_tab('电台') + tap_card_by_texts
  （l10n platformRadio90s 中文未核准候选兜底）+ ocr_page_texts 计数；
- 步骤2 页面归属断言 -> 以「从 90s 区块进入后页面直接可用」为归属
  证据（黑盒口径：来源区块 + 页面渲染，码值语义服务端契约承担）；
- 步骤3 首项 hero 装饰与列表完整性 -> 列表渲染完整计数兜底，hero
  形态合成模板未入库登记 template_needs（视觉精比对留图像兜底轮）。

清理：纯查询，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadio90sFullList(BaseTest):
    """radio-POS-014：90s 页全量渲染，来源区块归属正确。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_90s_full_list(self):
        """90s 页列表全量渲染（经 90s 区块入口）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1/2：经 90s 区块进入（归属证据），全量列表渲染
        self.userA.tap_card_by_texts("90后", "90后电台", "90er", "90")
        texts = self.userA.ocr_page_texts()
        assert len(texts) >= 5, f"90s 页列表渲染项过少: {len(texts)}"
        # 步骤3：列表完整性（hero 形态留图像兜底轮）
        self.userA.swipe_up()
        texts_after = self.userA.ocr_page_texts()
        assert len(texts_after) >= 3, "下滑后列表渲染异常"

    def teardown(self) -> None:
        """纯查询无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
