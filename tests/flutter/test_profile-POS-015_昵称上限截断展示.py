# CASE-ID: profile-POS-015
"""Swan 回归·M13 个人中心：昵称上限截断展示（profile-POS-015）。

用例 → AW 映射（B 级：修改昵称页 OCR 锚「修改昵称」）：
- 输入 12 字符串 → maxLength=10 截断：输入框仅回显前 10 字符
  text_exists("TEST昵称长度截断") + text_not_exists("TEST昵称长度截断AB")
- 不提交退出
清理（G3/G4）：全程未提交，昵称无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos015NicknameLimitTruncation(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_nickname_limit_truncation(self) -> None:
        self.userA.open_me_page()
        current = self.userA.me_top_nickname()
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        self.userA.focus_nickname_input(current)
        self.userA.clear_input()
        # 12 字符输入，前 10 字符保留
        self.userA.input_text("TEST昵称长度截断AB")
        self.userA.text_exists("TEST昵称长度截断", timeout=5)
        self.userA.text_not_exists("TEST昵称长度截断AB", timeout=3)
        self.userA.exit_edit_page_without_save()

    def teardown(self) -> None:
        pass
