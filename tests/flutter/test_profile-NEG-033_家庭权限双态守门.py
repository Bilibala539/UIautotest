# CASE-ID: profile-NEG-033
"""Swan 回归·M13 个人中心：家庭权限双态弹层守门（profile-NEG-033）。

用例 → AW 映射（C 级简化转换）：
- 创建人态分支（swanuserA 为「惠威2b11」家庭创建人）：
  「创建人」标识 OCR + 添加成员图标 [图] 存在；
  打开加成员弹层后取消即止（back 等效取消，不写数据）；
  改名入口条件探测（入口文案未探索，命中则打开后取消）
- 成员态分支：共享登录态账号为创建人，成员态视角需成员账号 → 执行注记（负向预标）
清理（G3/G4）：弹层均取消即止，家庭数据无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg033FamilyRoleGate(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_family_role_dialogs_gate(self) -> None:
        self.userA.open_me_page()
        self.userA.open_family_page()
        # 创建人态：「创建人」标识 + 添加成员入口 [图]
        self.userA.assert_any_text(["创建人"], timeout=5)
        self.userA.image_exists("SWAN_FAMILY_ADD_MEMBER_ICON", timeout=5)
        # 打开加成员弹层后取消即止
        self.userA.click_image("SWAN_FAMILY_ADD_MEMBER_ICON")
        self.userA.assert_page_not_blank()
        self.userA.press_back()
        self.userA.assert_any_text(["我的家庭"], timeout=5)
        # 改名入口条件探测（入口文案未探索：命中则打开后取消）
        for name in ("修改家庭名称", "改名", "家庭名称"):
            if self.userA.find_text_by_ocr(name, timeout=1) is not None:
                self.userA.click_text(name)
                self.userA.press_back()
                break
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
