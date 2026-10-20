# CASE-ID: profile-POS-010
"""Swan 回归·M13 个人中心：关于与升级行进入（profile-POS-010）。

用例 → AW 映射（A- 级）：
- 「关于与升级」行进入 → open_about_page（「软件升级」OCR 判据）
- 行渲染：关于我们/使用政策/隐私政策协议 + 版本行 OCR 提取
- 软件升级行零点击（不触发升级检查）；协议行点击进 H5 页锚未探索 → 模板需求登记
- back 返回我的页
清理（G3/G4）：只读断言无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos010AboutRowEntry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_about_row_entry(self) -> None:
        self.userA.open_me_page()
        self.userA.open_about_page()
        self.userA.text_exists("关于我们", timeout=5)
        self.userA.text_exists("使用政策", timeout=5)
        self.userA.text_exists("隐私政策协议", timeout=5)
        version_line = self.userA.about_version_text()
        assert version_line is not None, "关于页未 OCR 到版本行"
        # 软件升级行零点击
        self.userA.text_exists("软件升级", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
