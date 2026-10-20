# CASE-ID: profile-POS-003
"""Swan 回归·M13 个人中心：充值与消费记录页进入（profile-POS-003）。

用例 → AW 映射（B 级：目标页未探索）：
- 「充值与消费记录」行进入 → open_recharge_record（OCR 行 + assert_page_not_blank 兜底）
- back 返回我的页
- 页内容锚（订单/记录列表）未探索 → 模板需求已登记（充值记录页锚）
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos003RechargeRecordPage(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_recharge_record_page(self) -> None:
        self.userA.open_me_page()
        self.userA.open_recharge_record()
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
