# CASE-ID: profile-POS-007
"""Swan 回归·M13 个人中心：设备管理行进入（profile-POS-007）。

用例 → AW 映射（B 级：设备设置页锚未探索）：
- 「设备管理」行 [图] 进入（标题行与可点行重名，OCR 有歧义走 SWAN_ME_DEVICE_MANAGE_ROW 模板）
  → open_device_setting（assert_page_not_blank 兜底）
- back 返回我的页
- 页内容锚未探索 → 模板需求已登记（设备设置页锚）
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos007DeviceRowEntry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_device_setting_entry(self) -> None:
        self.userA.open_me_page()
        self.userA.open_device_setting()
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
