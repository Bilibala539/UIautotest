# CASE-ID: profile-POS-033
"""Swan 回归·M13 个人中心：顶卡与资料页数据同源（profile-POS-033）。

用例 → AW 映射（A- 级）：
- 我的页顶卡昵称 OCR 读取（me_top_nickname）+ 明文手机号
- 个人资料页昵称行/手机号行与顶卡一致（text_exists 同值）
- 返回后顶卡再比对（昵称字符串相等 + 手机号仍显）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos033TopCardPersonInfoConsistency(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_top_card_person_info_consistency(self) -> None:
        self.userA.open_me_page()
        nickname = self.userA.me_top_nickname()
        self.userA.text_exists(self.userA.phone, timeout=5)
        self.userA.open_person_info()
        self.userA.text_exists(nickname, timeout=5)
        self.userA.text_exists(self.userA.phone, timeout=5)
        self.userA.back_to_me_page()
        # 返回后顶卡仍同源
        assert self.userA.me_top_nickname() == nickname, "往返后顶卡昵称变化"
        self.userA.text_exists(self.userA.phone, timeout=5)

    def teardown(self) -> None:
        pass
