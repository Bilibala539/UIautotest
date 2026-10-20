# CASE-ID: profile-POS-022
"""Swan 回归·M13 个人中心：家庭创建人态浏览（profile-POS-022）。

用例 → AW 映射（B 级：swanuserA 为「惠威2b11」家庭创建人）：
- 家庭页到位（OCR「我的家庭」）→ open_family_page
- 创建人态标识 OCR「创建人」+ 添加成员入口 [图] 存在（零写：不点击）
- 右上角二维码图标无 OCR 文本且无注册模板 → 模板需求已登记（家庭页二维码图标）
- back 返回我的页
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos022FamilyCreatorBrowse(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_family_creator_browse(self) -> None:
        self.userA.open_me_page()
        self.userA.open_family_page()
        self.userA.assert_any_text(["创建人"], timeout=5)
        self.userA.image_exists("SWAN_FAMILY_ADD_MEMBER_ICON", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
