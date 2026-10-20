# CASE-ID: music-NEG-037
"""Swan 回归·M07 平台授权:AM 解绑语义≠他平台:仅隐藏本机,绑定保留(music-NEG-037)。

步骤→AW 映射(坑 2:AM 解绑只 isShow=0+清本机,不走 op=1;写操作全程止于
确认弹层——revoke no-op 族硬约束):
  1. AM 行点 [−] 发起取消授权至确认弹层 → tap_platform_row_minus('apple'),
     弹层以「确认」+「取消」双钮 [OCR] 探活(居中式)
  2. 核对语义提示文案(不点最终确认) → assert_any_text(['取消授权','隐藏',
     '不再展示','解绑'])(文案未标定,B 口径)
  3. 服务端预置解绑展示态(isShow=0+hasUserToken=1)+再授权免全 OAuth →
     专用账号后置轮职责,不落本用例(docstring 如实登记)
  4. 平台页 AM 态与预置一致 → 后置轮核对口径,本用例终止于弹层取消

cleanup: 点「取消」关闭弹层(写操作止步),断言 AM 行仍为已授权态
(取消解绑绑定保留);框架每用例冷启动。
B 标定说明:AM 行 [−] 钮 OCR 细横线不稳,模板真机补截后回填 row_template
实参;确认弹层语义文案标定后收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg037AmUnbindDialogOnly(BaseTest):
    """AM 解绑至确认弹层:语义提示核对后取消,绑定保留。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_am_unbind_stop_at_dialog(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("apple") != "authorized":
            pytest.skip(
                "Apple Music 行非已授权态(需已授权预置),解绑确认弹层无法发起"
                "(账号态自适配)")
        self.userA.tap_platform_row_minus("apple")
        assert self.userA.find_text_by_ocr("确认", timeout=6) is not None, (
            "AM 取消授权确认弹层未出现(「确认」钮未命中)")
        # 步骤 2:语义提示文案核对,不点击最终确认(写操作止步)
        self.userA.assert_any_text(["取消授权", "隐藏", "不再展示", "解绑"])
        # cleanup:点「取消」收束,绑定保留
        self.userA.click_text("取消", timeout=5)
        self.userA.assert_no_auth_error()
        assert self.userA.platform_row_state("apple") == "authorized", (
            "取消解绑后 AM 授权态变化(应保持已授权,绑定保留)")
