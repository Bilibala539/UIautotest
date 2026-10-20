# CASE-ID: login-POS-005
"""Swan 回归·会话与登录:密码形态共用区号选择入口(login-POS-005)。

步骤→AW 映射:
1. 切密码形态(ensure_password_form);
2. 点区号按钮「+86」进区号页(open_area_page) → 点中国整行([图])自动返回;
3. 断言落点=密码形态:密码框 [图] 命中、「验证码登入」[OCR] 在,
   且区号回填「+86」[OCR] 命中。
注:本条不提交,零短信成本;区号页与登录形态解耦的机制探针(YAML S3)为记录面。
cleanup: 未登录态保持,无遗留。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PASSWORD_FIELD
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestAreaEntrySharedAcrossForms(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_area_entry_shared_across_forms(self) -> None:
        # 步骤 1-2:密码形态进区号页选中国
        self.userA.ensure_fresh_sms_form()
        self.userA.ensure_password_form()
        self.userA.open_area_page("+86")
        self.userA.select_china_area_row()
        # 步骤 3:落点仍为密码形态且区号回填
        assert self.userA.find_text_by_ocr("+86", timeout=5) is not None, (
            "区号选择后未回填 +86")
        assert self.userA.find_image(SWAN_PASSWORD_FIELD, timeout=5) is not None, (
            "区号选择返回后未落回密码形态(密码框不可见)")
        assert self.userA.find_text_by_ocr("验证码登入", timeout=3) is not None, (
            "区号选择返回后密码形态回切钮不可见")
