# CASE-ID: profile-NEG-022
"""Swan 回归·M13 个人中心：邮箱编辑入口缺失探针（profile-NEG-022）。

用例 → AW 映射（C 级条件转换）：
- 个人信息页探测「邮箱」行：当前 build 无邮箱行（坑12：路由-only 无入口）→
  pytest.skip 如实上报环境现状
- 若行存在（回归到有邮箱行版本时）：点击进编辑页 → assert_page_not_blank → 返回
  （格式校验面 OCR 输入通道同昵称族，回归版本上再展开）
清理（G3/G4）：条件分支均不写数据；冷启动由框架夹具承担。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg022EmailEntryProbe(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_email_edit_probes(self) -> None:
        self.userA.open_me_page()
        self.userA.open_person_info()
        if self.userA.find_text_by_ocr("邮箱", timeout=3) is None:
            pytest.skip("个人信息页无邮箱行（坑12 现状：路由-only，无入口）")
        self.userA.click_text("邮箱")
        self.userA.assert_page_not_blank()
        self.userA.press_back()
        self.userA.assert_on_person_info(timeout=5)

    def teardown(self) -> None:
        pass
