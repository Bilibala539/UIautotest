# CASE-ID: login-NEG-001
"""Swan 回归·会话与登录:协议取消再提交 门控翻转置灰+号码保留(login-NEG-001)。

步骤→AW 映射:
1. 填 11 位手机号 + 勾协议 → fill_phone_number + accept_agreement(两态图幂等),
   断言主按钮置灰解除(SWAN_LOGIN_SUBMIT_ENABLED 可用态图 [图] 命中);
2. 取消勾选 → cancel_agreement(点已选态图翻转),断言主按钮回到置灰;
3. 手机号保留 → [OCR] 完整号码「13555555555」仍可在页内命中(协议操作不清号码);
4. 重新勾选后点主按钮 → 点击可用态图,断言进入验证码输入页(输入框 [图] 命中)。
cleanup: 未登录态保持;用例末已进入输码页,冷启动模型由框架复位,不做进程内回退。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_LOGIN_CODE_FIELD_BOX,
    SWAN_LOGIN_SUBMIT_ENABLED,
)
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestAgreementCancelGating(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_agreement_cancel_gating(self) -> None:
        # 步骤 1:填号 + 勾协议 → 门控解除
        self.userA.ensure_fresh_sms_form()
        self.userA.fill_phone_number("13555555555")
        self.userA.accept_agreement()
        self.userA.assert_sms_submit_enabled(True)
        # 步骤 2:取消勾选 → 门控翻回置灰
        self.userA.cancel_agreement()
        self.userA.assert_sms_submit_enabled(False)
        # 步骤 3:手机号文本保留(OCR 命中完整号码)
        assert self.userA.find_text_by_ocr("13555555555", timeout=5) is not None, (
            "取消勾选后手机号被清空(协议操作不应影响号码)")
        # 步骤 4:重新勾选 + 点击主按钮 → 进入验证码输入页
        self.userA.accept_agreement()
        self.userA.click_image(SWAN_LOGIN_SUBMIT_ENABLED, timeout=10)
        assert self.userA.find_image(SWAN_LOGIN_CODE_FIELD_BOX, timeout=15) is not None, (
            "重新勾选协议后提交未进入验证码输入页(门控未恢复推进)")
