# CASE-ID: profile-POS-013
"""Swan 回归·M13 个人中心：个人资料页六区块展示（profile-POS-013）。

用例 → AW 映射（A- 级，区块=顶卡镜像+行组）：
- 昵称行与顶卡同源：me_top_nickname 读取后 text_exists
- 密码行（掩码展示，标签 OCR「密码」）、手机号行（text_exists(userA.phone)）
- 账号绑定管理行条件探测（有绑定态才显示 → 记录）
- 「注销账号」入口 + 「退出登入」[图]（页面锚）
- 头像缩略图无 OCR 文本且无注册模板 → 模板需求已登记（头像缩略图锚）
清理（G3/G4）：零点击只读断言；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos013PersonInfoBlocks(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_person_info_blocks_render(self) -> None:
        self.userA.open_me_page()
        nickname = self.userA.me_top_nickname()
        self.userA.open_person_info()
        # 昵称行（与顶卡同源）
        self.userA.text_exists(nickname, timeout=5)
        # 密码行（掩码）与手机号行
        self.userA.text_exists("密码", timeout=5)
        self.userA.text_exists(self.userA.phone, timeout=5)
        # 账号绑定管理行（条件显隐，探测记录）
        self.userA.find_text_by_ocr("账号绑定管理", timeout=2)
        # 危险区入口
        self.userA.text_exists("注销账号", timeout=5)
        self.userA.image_exists("SWAN_PERSON_LOGOUT_BTN", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
