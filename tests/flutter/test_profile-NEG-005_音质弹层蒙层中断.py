# CASE-ID: profile-NEG-005
"""Swan 回归·M13 个人中心：音质弹层蒙层关闭中断（profile-NEG-005）。

用例 → AW 映射：
- 打开音质弹层 → open_quality_sheet（行 [图] + OCR 档位判据）
- 四档行渲染 → assert_quality_tiers（流畅/标准/HQ/SQ）
- 选 HQ 高品质 → select_quality_tier("HQ高品质")
- 不点完成、点蒙层关闭 → 蒙层无文本不可 OCR 定位，back 键等效替代
  （close_quality_sheet_by_back，notes 已记差异）
- 重开弹层四档仍在 → assert_quality_tiers
  （选中态 O 型单选圈 OCR 不可辨，KV 脏值不可观察 → 模板需求已登记）
清理（G3/G4）：未提交选择即关闭，无 KV 写入；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg005QualityMaskInterrupt(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_quality_sheet_mask_close_interrupt(self) -> None:
        self.userA.open_me_page()
        self.userA.open_quality_sheet()
        self.userA.assert_quality_tiers()
        self.userA.select_quality_tier("HQ高品质")
        # 蒙层点击的免坐标等效替代：back 键关闭弹层
        self.userA.close_quality_sheet_by_back()
        # 重开弹层：四档行仍在
        self.userA.open_quality_sheet()
        self.userA.assert_quality_tiers()
        self.userA.close_quality_sheet_by_back()

    def teardown(self) -> None:
        pass
