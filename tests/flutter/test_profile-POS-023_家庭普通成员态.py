# CASE-ID: profile-POS-023
"""Swan 回归·M13 个人中心：家庭普通成员态浏览（profile-POS-023）。

用例 → AW 映射（B 级条件转换）：
- 成员态前提：账号非创建人。共享登录态 swanuserA 为「惠威2b11」创建人 →
  探测「创建人」标识命中即 pytest.skip（成员态视角需成员账号，如实上报）
- 成员态可自动化面：添加成员入口 [图] 不应出现（权限越界负向断言）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos023FamilyMemberState(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_family_member_state_browse(self) -> None:
        self.userA.open_me_page()
        self.userA.open_family_page()
        if self.userA.find_text_by_ocr("创建人", timeout=3) is not None:
            pytest.skip("当前账号为创建人态（swanuserA 为家庭创建人），成员态视角需成员账号")
        # 成员态：不应出现创建人专属「添加成员」入口
        assert self.userA.find_image("SWAN_FAMILY_ADD_MEMBER_ICON", timeout=3) is None, \
            "成员态出现创建人专属「添加成员」入口（权限越界）"
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
