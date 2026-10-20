# CASE-ID: profile-NEG-039
"""Swan 回归·M13 个人中心：我的页无消息中心入口（profile-NEG-039）。

用例 → AW 映射（薄 A：负向存在性断言）：
- 我的页全页滚动 OCR 扫描 → 「消息中心」入口不应存在
  （坑9：消息中心无 UI 入口，与产品口径一致）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg039MessageCenterNoEntry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_message_center_no_entry(self) -> None:
        self.userA.open_me_page()
        # 全页滚动探测：不得出现「消息中心」入口
        assert not self.userA.me_row_scroll_until("消息中心"), \
            "我的页出现「消息中心」入口（与知识库坑9 口径冲突）"

    def teardown(self) -> None:
        pass
