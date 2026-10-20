# CASE-ID: profile-POS-014
"""Swan 回归·M13 个人中心：昵称编辑主路径（profile-POS-014）。

用例 → AW 映射（B 级：修改昵称页 OCR 锚「修改昵称」+「完成」）：
- 空值守门复验：clear_input + 点「完成」→ 被拒仍在编辑页
- 合法值输入（≤10 字符）：输入框回显通过态 text_exists("TEST昵称QA01")
- 不提交退出（避免污染共享账号昵称；成功提交面由灰度账号专项承担）
清理（G3/G4）：全程未提交，昵称无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos014NicknameEditMainPath(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_nickname_edit_main_path(self) -> None:
        self.userA.open_me_page()
        current = self.userA.me_top_nickname()
        self.userA.open_person_info()
        self.userA.open_edit_nickname()
        # 空值守门复验
        self.userA.focus_nickname_input(current)
        self.userA.clear_input()
        self.userA.click_text("完成", timeout=5)
        self.userA.text_exists("修改昵称", timeout=3)
        # 合法值通过态（输入框回显）
        self.userA.input_text("TEST昵称QA01")
        self.userA.text_exists("TEST昵称QA01", timeout=5)
        # 不提交退出
        self.userA.exit_edit_page_without_save()

    def teardown(self) -> None:
        pass
