# CASE-ID: profile-POS-012
"""Swan 回归·M13 个人中心：扫一扫发起扫码链（profile-POS-012）。

用例 → AW 映射（A- 级）：
- 顶卡扫一扫图标 [图]（SWAN_ME_SCAN_ICON，坑15 无语义键）→ open_scan_page
- 扫码页到位：OCR 标题「扫一扫」+ 相机取景提示「放入框内」
- back 返回我的页
- 实际扫码识别面（合法二维码内容解析）→ 见 profile-POS-021 授权链与本包跳过项注记
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos012ScanLaunch(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_scan_launch(self) -> None:
        self.userA.open_me_page()
        self.userA.open_scan_page()
        # 相机取景提示（知识库 dump OCR 实录「将二维码/条码放入框内」）
        self.userA.assert_any_text(["放入框内"], timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
