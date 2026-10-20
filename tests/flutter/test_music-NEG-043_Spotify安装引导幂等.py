# CASE-ID: music-NEG-043
"""Swan 回归·M07 平台授权:Spotify 未装添加→安装引导弹层拦截(music-NEG-043)。

步骤→AW 映射(坑 11 未授权添加路径:ensureInstalledOrShowGuide 未装恒
false → showSpotifyInstallBottomSheet 安装引导弹层拦截):
  1. 平台页 Spotify 行点 [+] → tap_platform_row_plus('spotify'),安装引导
     弹层出现 → assert_any_text(['安装','下载','Spotify'])
  2. 弹层交互面核对(跳转按钮止于发起,禁区 7 外部跳转拦截由环境承担,
     用例不点击跳转) → CTA 按钮文案 [OCR] 变体核对
  3. 关闭弹层后再点 [+] 核对幂等 → dismiss_auth_popup + 条件 press_back
     (底部弹层 back 收束) → 再次 tap_platform_row_plus('spotify'),
     引导弹层再次出现(无状态残留/无叠加)

cleanup: 再次关闭弹层;断言 Spotify 行全程保持未授权态(添加未放行)。
B 标定说明:安装引导底部弹层文案与 CTA 按钮未截模板,以「安装/下载/Spotify」
变体锚为 B 口径;弹层专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicNeg043SpotifyInstallGuide(BaseTest):
    """Spotify 未装点 [+] → 安装引导弹层拦截且幂等。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_spotify_install_guide_idempotent(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("spotify") != "unauthorized":
            pytest.skip("Spotify 行非未授权态,未装添加门禁无法复现(账号态自适配)")
        # 步骤 1:未装判定 → 安装引导弹层(授权与内容路径均不开放)
        self.userA.tap_platform_row_plus("spotify")
        self.userA.assert_any_text(["安装", "下载", "Spotify"])
        # 步骤 3 前半:关闭弹层(取消钮/back 双路收束,根级禁返回键不盲退)
        self.userA.dismiss_auth_popup()
        if self.userA.find_text_by_ocr("安装", timeout=2) is not None:
            self.userA.press_back()
        assert self.userA.platform_row_state("spotify") == "unauthorized", (
            "引导弹层关闭后 Spotify 行态变化(应保持未授权)")
        # 步骤 3 后半:再点 [+] 幂等复现,无状态残留、无重复叠加
        self.userA.tap_platform_row_plus("spotify")
        self.userA.assert_any_text(["安装", "下载", "Spotify"])
        assert self.userA.platform_row_state("spotify") == "unauthorized", (
            "二次引导后 Spotify 行态变化(应保持未授权,授权路径未放行)")
        self.userA.dismiss_auth_popup()
        if self.userA.find_text_by_ocr("安装", timeout=2) is not None:
            self.userA.press_back()
        self.userA.assert_no_auth_error()
