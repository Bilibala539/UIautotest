# CASE-ID: music-NEG-003
"""Swan 回归·M07 平台授权:QQ 授权挂起超 120 秒→超时兜底自动收束(music-NEG-003)。

步骤→AW 映射:
  1. 发起 QQ 授权并保持挂起(全程不点取消) → tap_platform_row_plus('qq')
     + confirm_auth_dialog(),进度弹层以「取消」钮 [OCR] 探活
  2. 纯等待超时兜底 → find_text_by_ocr('取消', timeout=150) 有界轮询至弹层
     自动关闭(非硬等待;坑 7:120s 超时以 user_cancel 类结果收束;用例全程
     ≥130s,为全包最长用例)
  3. 平台页无错误提示 → assert_no_auth_error()(静默类)
  4. 再次发起不被 auth_in_progress 阻塞 → 再次 tap_platform_row_plus('qq')
     + confirm_auth_dialog(),挂起链路可重建(进度弹层再现)

cleanup: dismiss_auth_popup 取消第二次挂起授权,回平台页;框架每用例冷启动。
B 标定说明:环境侧需 QQ 回跳被拦截(未装/不响应);若超时窗口内授权被环境
侧真实完成(行态转已授权),第 4 步前置失真,按账号态自适配跳过。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg003AuthTimeoutFallback(BaseTest):
    """QQ 挂起 120s 超时兜底:自动收束,授权锁释放可重入。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_pending_timeout_fallback_releasable(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "unauthorized":
            pytest.skip("QQ 行非未授权态,授权挂起链路无法从 [+] 发起(账号态自适配)")
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
            "确认后授权进度弹层未出现(第一次授权未进入挂起)")
        assert self.userA.find_text_by_ocr("取消", timeout=150) is None, (
            "150s 内进度弹层未自动收束(120s 超时兜底未生效或弹层卡死)")
        self.userA.assert_no_auth_error()
        if self.userA.platform_row_state("qq") != "unauthorized":
            pytest.skip(
                "超时窗口内授权被环境侧完成(行态转已授权),挂起锁释放的"
                "重入前置失真(账号态自适配)")
        self.userA.tap_platform_row_plus("qq")
        self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("取消", timeout=10) is not None, (
            "超时收束后再次发起授权未进入挂起(进度弹层未现,疑 auth_in_progress 误锁)")
        self.userA.dismiss_auth_popup()
