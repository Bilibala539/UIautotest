# CASE-ID: profile-POS-002
"""Swan 回归·M13 个人中心：顶卡进个人资料页（profile-POS-002）。

用例 → AW 映射（A 级主路径）：
- 顶卡用户区 [图] → 个人资料页（open_person_info，到位锚「退出登入」[图]）
- 手机号行明文展示 → text_exists(userA.phone)
- 「注销账号」入口渲染 → text_exists
- back 返回我的页
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos002TopCardToPersonInfo(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_top_card_to_person_info(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        self.userA.text_exists(self.userA.phone, timeout=5)
        self.userA.image_exists("SWAN_PERSON_LOGOUT_BTN", timeout=5)
        self.userA.text_exists("注销账号", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
