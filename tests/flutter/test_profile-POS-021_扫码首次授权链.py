# CASE-ID: profile-POS-021
"""Swan 回归·M13 个人中心：扫码首次授权链（profile-POS-021）。

用例 → AW 映射（B 级：系统权限弹窗 ROM 文案变体轮询）：
- 首点扫一扫图标 [图] → 系统权限弹窗 → 点「允许」系变体（handle_camera_permission）
- 弹窗未出现（权限已授予）→ 继续直达扫码页（授予态由平台预置，注记）
- 到位断言：OCR 标题「扫一扫」+ 取景提示「放入框内」
- back 返回我的页
清理（G3/G4）：授权为用户预期内状态；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos021ScanFirstAuthorize(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_scan_first_authorize(self) -> None:
        self.userA.open_me_page()
        self.userA.click_image("SWAN_ME_SCAN_ICON")
        # 弹窗未出现 = 权限已授予，直达扫码页
        self.userA.handle_camera_permission(allow=True)
        self.userA.text_exists("扫一扫", timeout=10)
        self.userA.assert_any_text(["放入框内"], timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
