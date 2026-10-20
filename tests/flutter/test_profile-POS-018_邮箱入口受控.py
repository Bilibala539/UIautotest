# CASE-ID: profile-POS-018
"""Swan 回归·M13 个人中心：邮箱入口受控（profile-POS-018）。

用例 → AW 映射（薄 A：负向存在性断言）：
- 个人资料页无「邮箱」行（坑12 现状：路由-only 无入口）→ text_not_exists 负向断言
  （未来版本若补该行，本断言失败=口径漂移提示，属正确暴露）
- 深链路由直访面需深链注入通道 → 执行注记（SKIP-INFRA）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos018EmailEntryControlled(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_email_entry_controlled(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        self.userA.text_not_exists("邮箱", timeout=3)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
