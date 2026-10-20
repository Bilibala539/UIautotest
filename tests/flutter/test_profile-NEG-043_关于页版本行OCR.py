# CASE-ID: profile-NEG-043
"""Swan 回归·M13 个人中心：关于页版本行 OCR 定位（profile-NEG-043）。

用例 → AW 映射（A- 级）：
- 进入关于页 → open_about_page（「软件升级」OCR 判据）
- 版本行 OCR 提取（含「版本」关键字文本项，如「版本5.3.0 (build 32) profile -test」）
  → about_version_text + 截图留档由框架上报通道自动完成
- 软件升级行存在且零点击（不触发升级检查流程）
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg043AboutVersionOcr(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_about_version_ocr(self) -> None:
        self.userA.open_me_page()
        self.userA.open_about_page()
        # 版本行 OCR 提取（两行版本信息以首个含「版本」文本项为准）
        version_line = self.userA.about_version_text()
        assert version_line is not None, "关于页未 OCR 到版本行（含「版本」关键字）"
        # 软件升级行存在，零点击
        self.userA.text_exists("软件升级", timeout=5)

    def teardown(self) -> None:
        pass
