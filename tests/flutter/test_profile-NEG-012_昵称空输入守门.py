# CASE-ID: profile-NEG-012
"""Swan 回归·M13 个人中心：昵称空输入族守门（profile-NEG-012）。

用例 → AW 映射（B 级：修改昵称页为独立页，OCR 锚「修改昵称」+「完成」）：
- 进编辑页 → open_me_page → me_top_nickname 取当前昵称 → open_person_info → open_edit_nickname
- 变体1 全空：focus_nickname_input + clear_input + 点「完成」→ 空值被拒仍在编辑页
  （若空值被成功提交即页面弹出，断言失败=缺陷暴露）
- 变体2 纯半角空格 / 变体3 全角空格+制表符：同样被拒
- 不提交退出 → exit_edit_page_without_save（绝不点完成，杜绝误保存）
清理（G3/G4）：全程未提交，昵称无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg012NicknameEmptyGate(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_nickname_empty_input_gate(self) -> None:
        self.userA.open_me_page()
        current = self.userA.me_top_nickname()
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        # 变体1：全空
        self.userA.focus_nickname_input(current)
        self.userA.clear_input()
        self.userA.click_text("完成", timeout=5)
        self.userA.text_exists("修改昵称", timeout=3)
        # 变体2：纯半角空格
        self.userA.clear_input()
        self.userA.input_text("   ")
        self.userA.click_text("完成", timeout=5)
        self.userA.text_exists("修改昵称", timeout=3)
        # 变体3：全角空格+制表符
        self.userA.clear_input()
        self.userA.input_text("　\t ")
        self.userA.click_text("完成", timeout=5)
        self.userA.text_exists("修改昵称", timeout=3)
        # 不提交退出
        self.userA.exit_edit_page_without_save()

    def teardown(self) -> None:
        pass
