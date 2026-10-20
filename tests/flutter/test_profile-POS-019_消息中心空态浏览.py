# CASE-ID: profile-POS-019
"""Swan 回归·M13 个人中心：消息中心入口缺失现状（profile-POS-019）。

用例 → AW 映射（薄 A：负向存在性断言；坑9 无 UI 入口）：
- 我的页全页滚动 OCR 扫描 → 「消息中心」入口不应存在
- （消息中心页本体跳过：无入口且页锚未探索，见包报告注记）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos019MessageCenterAbsent(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_message_center_absent(self) -> None:
        self.userA.open_me_page()
        assert not self.userA.me_row_scroll_until("消息中心"), \
            "我的页出现「消息中心」入口（坑9 口径漂移）"

    def teardown(self) -> None:
        pass
