# CASE-ID: music-NEG-038
"""Swan 回归·M07 平台授权:网易云/酷狗解绑 revoke no-op:断言口径=服务端态(music-NEG-038)。

步骤→AW 映射(坑 1 revoke no-op 族:网易云/酷狗解绑只有服务端 op=1 有效,
本地 revoke 静默;解绑止于确认弹层硬约束,执行轮不对本地会话清理做断言):
  1. 网易云行点 [−] 至确认弹层 → tap_platform_row_minus('netease'),
     「确认」+「取消」双钮 [OCR] 探活
  2. 确认后服务端 op=1+isShow=0 生效核对 → 专用账号后置轮职责,不落本用例
     (data 标注"后置轮断言");本用例点「取消」止步
  3. 酷狗同流程至确认弹层 → tap_platform_row_minus('kugou')(行态自适配)
  4. 断言面=服务端态与平台页展示态 → 口径登记见 docstring,不在执行轮断言

cleanup: 各弹层点「取消」关闭(写操作止步),断言行态保持已授权;框架每用例
冷启动。
B 标定说明:网易云/酷狗行 [−] 钮 OCR 细横线不稳,模板真机补截后回填
row_template 实参(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg038UnbindDialogServerState(BaseTest):
    """网易云/酷狗解绑至确认弹层:取消止步,行态保持,断言口径=服务端态。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_kugou_unbind_dialog(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        ran = False
        if self.userA.platform_row_state("netease") == "authorized":
            # 步骤 1:网易云解绑至确认弹层(已授权态闸门在 helper 内)
            self.userA.tap_platform_row_minus("netease")
            assert self.userA.find_text_by_ocr("确认", timeout=6) is not None, (
                "网易云取消授权确认弹层未出现(「确认」钮未命中)")
            self.userA.click_text("取消", timeout=5)
            self.userA.assert_no_auth_error()
            assert self.userA.platform_row_state("netease") == "authorized", (
                "取消解绑后网易云行态变化(应保持已授权)")
            ran = True
        if self.userA.platform_row_state("kugou") == "authorized":
            # 步骤 3:酷狗同流程至确认弹层
            self.userA.tap_platform_row_minus("kugou")
            assert self.userA.find_text_by_ocr("确认", timeout=6) is not None, (
                "酷狗取消授权确认弹层未出现(「确认」钮未命中)")
            self.userA.click_text("取消", timeout=5)
            self.userA.assert_no_auth_error()
            assert self.userA.platform_row_state("kugou") == "authorized", (
                "取消解绑后酷狗行态变化(应保持已授权)")
            ran = True
        if not ran:
            pytest.skip(
                "网易云/酷狗行均非已授权态,解绑确认弹层无法发起(账号态自适配)")
