# CASE-ID: profile-NEG-013
"""Swan 回归·M13 个人中心：昵称 10 字符上限截断（profile-NEG-013）。

用例 → AW 映射（B 级：修改昵称页 OCR 锚「修改昵称」）：
- 输入 11 字符串 → 输入框仅保留前 10 字符：text_exists(前10字) + text_not_exists(全11字)
- emoji 输入页面不崩溃（存活判据 OCR 标题仍在）
- 不提交退出 → exit_edit_page_without_save
清理（G3/G4）：全程未提交，昵称无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg013NicknameTenCharLimit(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_nickname_ten_char_limit(self) -> None:
        self.userA.open_me_page()
        current = self.userA.me_top_nickname()
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        self.userA.focus_nickname_input(current)
        self.userA.clear_input()
        # 输入 11 字符串：maxLength 截断为前 10 字符
        self.userA.input_text("测试昵称边界十个字整界")
        self.userA.text_exists("测试昵称边界十个字整", timeout=5)
        self.userA.text_not_exists("测试昵称边界十个字整界", timeout=3)
        # emoji 输入不崩溃（页面存活）
        self.userA.clear_input()
        self.userA.input_text("\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466")
        self.userA.text_exists("修改昵称", timeout=3)
        # 不提交退出
        self.userA.exit_edit_page_without_save()

    def teardown(self) -> None:
        pass
