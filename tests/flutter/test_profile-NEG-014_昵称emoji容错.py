# CASE-ID: profile-NEG-014
"""Swan 回归·M13 个人中心：昵称 emoji/组合字符容错（profile-NEG-014）。

用例 → AW 映射（B 级：修改昵称页 OCR 锚「修改昵称」）：
- 单 emoji（😀）、ZWJ 家庭组合（👨‍👩‍👧‍👦，源码用码点转义）、肤色修饰符（👍🏻）、
  RTL 控制符（U+202E）依次输入 → 每次页面存活（OCR 标题仍在，无崩溃/闪退）
- NUL 控制字符 adb 输入通道不可达 → 执行注记（notes）
- 不提交退出 → exit_edit_page_without_save
清理（G3/G4）：全程未提交，昵称无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg014NicknameEmojiTolerance(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_nickname_emoji_input_tolerance(self) -> None:
        self.userA.open_me_page()
        current = self.userA.me_top_nickname()
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        self.userA.focus_nickname_input(current)
        # 变体1：单 emoji
        self.userA.clear_input()
        self.userA.input_text("\U0001F600")
        self.userA.text_exists("修改昵称", timeout=3)
        # 变体2：ZWJ 家庭组合 emoji
        self.userA.clear_input()
        self.userA.input_text("\U0001F468‍\U0001F469‍\U0001F467‍\U0001F466")
        self.userA.text_exists("修改昵称", timeout=3)
        # 变体3：肤色修饰符组合
        self.userA.clear_input()
        self.userA.input_text("\U0001F44D\U0001F3FB")
        self.userA.text_exists("修改昵称", timeout=3)
        # 变体4：RTL 控制符（NUL 字符 adb 输入通道不可达，见执行注记）
        self.userA.clear_input()
        self.userA.input_text("‮abc")
        self.userA.text_exists("修改昵称", timeout=3)
        # 不提交退出
        self.userA.exit_edit_page_without_save()

    def teardown(self) -> None:
        pass
