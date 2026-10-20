# CASE-ID: profile-POS-025
"""Swan 回归·M13 个人中心：区号选择回填（profile-POS-025）。

用例 → AW 映射（B 级条件链，中间页锚未探索）：
- 链路：充值与消费记录 → 「发票」入口 → 「区号」入口 → 中国区号行 [图] 选择 →
  回填断言 OCR「+86」
- 任一链节点缺失（无预置订单/页锚漂移）→ pytest.skip 如实上报 + 模板需求登记
- 逐级回退到我的页（层级未探索，按落点判定）
清理（G3/G4）：区号选择为默认值回写，无状态变更；冷启动由框架夹具承担。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos025AreaCodeSelect(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_area_code_select(self) -> None:
        self.userA.open_me_page()
        self.userA.open_recharge_record()
        if self.userA.find_text_by_ocr("发票", timeout=3) is None:
            self.userA.back_to_me_page()
            pytest.skip("充值记录页无「发票」入口（无预置订单，数据依赖）")
        self.userA.click_text("发票")
        self.userA.assert_page_not_blank()
        if self.userA.find_text_by_ocr("区号", timeout=3) is None:
            self.userA.press_back()
            self.userA.back_to_me_page()
            pytest.skip("发票页无「区号」入口（页锚未探索，模板需求已登记）")
        self.userA.click_text("区号")
        self.userA.image_exists("SWAN_AREA_CODE_CHINA_ROW", timeout=5)
        self.userA.click_image("SWAN_AREA_CODE_CHINA_ROW")
        self.userA.text_exists("+86", timeout=5)
        # 逐级回退到我的页
        self.userA.press_back()
        if self.userA.find_text_by_ocr("发票", timeout=2) is not None:
            self.userA.press_back()
        if self.userA.find_text_by_ocr("充值", timeout=2) is not None:
            self.userA.press_back()
        self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=10)

    def teardown(self) -> None:
        pass
