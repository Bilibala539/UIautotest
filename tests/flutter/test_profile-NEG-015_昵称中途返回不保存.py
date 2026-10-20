# CASE-ID: profile-NEG-015
"""Swan 回归·M13 个人中心：昵称编辑中途返回不保存（profile-NEG-015）。

用例 → AW 映射（B 级：修改昵称页 OCR 锚「修改昵称」）：
- 输入新值后中途返回 → exit_edit_page_without_save（back 逐级回退，绝不点完成）
- 重新进入编辑页 → open_person_info + open_edit_nickname
- 断言 typed 值未持久化 → text_not_exists("中途放弃昵称abc")
-（顶卡昵称未变的二次确认见 profile-POS-033 同源比对，此处不重复断）
清理（G3/G4）：全程未提交，昵称无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg015NicknameAbandonNotSaved(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_nickname_edit_abandon_not_saved(self) -> None:
        self.userA.open_me_page()
        current = self.userA.me_top_nickname()
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        self.userA.focus_nickname_input(current)
        self.userA.clear_input()
        self.userA.input_text("中途放弃昵称abc")
        # 中途返回不提交
        self.userA.exit_edit_page_without_save()
        # 重新进入编辑页：typed 值不应存在
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        self.userA.text_not_exists("中途放弃昵称abc", timeout=3)
        self.userA.exit_edit_page_without_save()

    def teardown(self) -> None:
        pass
