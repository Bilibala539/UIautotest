# CASE-ID: profile-POS-005
"""Swan 回归·M13 个人中心：家庭管理行进入（profile-POS-005）。

用例 → AW 映射（A- 级）：
- 「家庭管理」行进入 → open_family_page（OCR 行 + 「我的家庭」判据）
- 页面存活锚：添加成员图标 [图]（SWAN_FAMILY_ADD_MEMBER_ICON）
- 右上角二维码图标无 OCR 文本且无注册模板 → 模板需求已登记（家庭页二维码图标）
- back 返回我的页
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos005FamilyRowEntry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_family_row_entry(self) -> None:
        self.userA.open_me_page()
        self.userA.open_family_page()
        self.userA.image_exists("SWAN_FAMILY_ADD_MEMBER_ICON", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
