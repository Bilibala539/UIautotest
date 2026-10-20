# CASE-ID: profile-NEG-028
"""Swan 回归·M13 个人中心：扫一扫相机权限拒绝守门（profile-NEG-028）。

用例 → AW 映射（B 级：系统权限弹窗 ROM 文案变体轮询）：
- 首点扫一扫 → 系统权限弹窗 → 点「拒绝」系变体 → 停留我的页（知识库实测口径）
- 弹窗未出现（权限已授予态无法构造首点拒绝）→ pytest.skip 如实上报
- 再次点击：仍被守门或进入错误态，返回我的页无崩溃
清理（G3/G4）：未授予权限，状态无变化；冷启动由框架夹具承担。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg028ScanPermissionDeny(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_scan_permission_deny(self) -> None:
        self.userA.open_me_page()
        self.userA.click_image("SWAN_ME_SCAN_ICON")
        if not self.userA.handle_camera_permission(allow=False):
            pytest.skip("系统相机权限弹窗未出现（权限已授予，无法构造首点拒绝态）")
        # 拒绝后停留我的页
        self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=10)
        # 再次点击扫一扫：仍被守门（弹窗复现再拒 / 系统记住拒绝态直接退回）
        self.userA.click_image("SWAN_ME_SCAN_ICON")
        if self.userA.handle_camera_permission(allow=False):
            self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=10)
        else:
            self.userA.press_back()
            self.userA.image_exists("SWAN_ME_FAVORITES_ROW", timeout=10)

    def teardown(self) -> None:
        pass
