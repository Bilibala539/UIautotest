# CASE-ID: profile-POS-030
"""Swan 回归·M13 个人中心：音质档位回写与还原（profile-POS-030）。

用例 → AW 映射（B 级：选中态 O 型单选圈 OCR 不可辨 → 模板需求已登记）：
- 打开弹层四档渲染 → open_quality_sheet + assert_quality_tiers
- 选「HQ高品质」→ 红字「完成」[图] 提交（confirm_quality_sheet，档位行不可见即关闭）
- 重开弹层四档仍在（回写成功的存活面；初始档比对不可 OCR 观察 → 执行注记）
- 还原「标准音质」→ 完成提交（共享账号默认档还原）
清理（G3/G4）：已还原标准档；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos030QualityWritebackRestore(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_quality_tier_writeback_restore(self) -> None:
        self.userA.open_me_page()
        self.userA.open_quality_sheet()
        self.userA.assert_quality_tiers()
        # 选 HQ 高品质并提交
        self.userA.select_quality_tier("HQ高品质")
        self.userA.confirm_quality_sheet()
        # 重开弹层：四档仍在（回写存活面）
        self.userA.open_quality_sheet()
        self.userA.assert_quality_tiers()
        # 还原标准音质并提交
        self.userA.select_quality_tier("标准音质")
        self.userA.confirm_quality_sheet()
        # 复验弹层可再开且稳定
        self.userA.open_quality_sheet()
        self.userA.assert_quality_tiers()
        self.userA.close_quality_sheet_by_back()

    def teardown(self) -> None:
        pass
