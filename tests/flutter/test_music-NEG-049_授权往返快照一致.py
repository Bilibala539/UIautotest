# CASE-ID: music-NEG-049
"""Swan 回归·M07 平台授权:授权页与平台页多次往返→授权态快照一致(music-NEG-049)。

步骤→AW 映射(坑 19 快照一致性家族,H5 WebView↔平台页往返):
  1. 发起网易云授权进 H5 授权页再返回,循环 3 次 → 每轮 tap_platform_row_plus
     ('netease', template=SWAN_NETEASE_PLUS_BTN) + confirm 探测 → 「登录」锚
     → press_back() → 「QQ音乐」行锚回平台页;每轮同构即状态一致,无叠加
  2. 第 3 次往返后核对快照 → assert_no_auth_error() + platform_row_state
     ('netease') 仍未授权(授权态未漂移)
  3. 中途取消一次后再完整走一次 → 确认弹层点「取消」→ 重发起全流程至 H5
     (取消与重入互不污染)

cleanup: H5 已退,无残留弹层即不再动作(根级禁返回键);框架每用例冷启动。
B 标定说明:网易云 H5 登录页锚用通用文案「登录」,真机补截后收紧;YAML
"弹层可拖拽/点外关闭"语义需弹层外坐标手势,受禁硬编码坐标约束不落用例
(见 package_report.json notes);测试账号已授权网易云为环境常态时自适配跳过。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_NETEASE_PLUS_BTN


class TestMusicNeg049AuthRoundtripSnapshot(BaseTest):
    """H5 授权页↔平台页多次往返:授权态快照一致,取消与重入互不污染。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_auth_roundtrip_snapshot_consistent(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("netease") != "unauthorized":
            pytest.skip(
                "网易云行非未授权态(测试账号已授权网易云为环境常态),"
                "H5 授权无法从 [+] 发起(账号态自适配)")
        # 步骤 1:发起→H5→返回,循环 3 次
        for _ in range(3):
            self.userA.tap_platform_row_plus(
                "netease", template=SWAN_NETEASE_PLUS_BTN)
            if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
                self.userA.confirm_auth_dialog()
            assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
                "往返中 H5 外域登录页未出现(WebView 未拉起)")
            self.userA.press_back()
            assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
                "往返中未回到平台页(WebView 未关闭)")
        # 步骤 2:第 3 次往返后快照核对(授权态未漂移)
        self.userA.assert_no_auth_error()
        assert self.userA.platform_row_state("netease") == "unauthorized", (
            "3 次往返后网易云授权态漂移(应保持未授权)")
        # 步骤 3 前半:中途取消一次(确认弹层点取消,或直达 H5 后系统返回)
        self.userA.tap_platform_row_plus("netease", template=SWAN_NETEASE_PLUS_BTN)
        if self.userA.find_text_by_ocr("取消", timeout=4) is not None:
            self.userA.click_text("取消", timeout=3)
        else:
            self.userA.press_back()
            assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
                "中途取消后未回到平台页")
        # 步骤 3 后半:完整走一次确认弹层(取消与重入互不污染)
        self.userA.tap_platform_row_plus("netease", template=SWAN_NETEASE_PLUS_BTN)
        if self.userA.find_text_by_ocr("确认", timeout=4) is not None:
            self.userA.confirm_auth_dialog()
        assert self.userA.find_text_by_ocr("登录", timeout=25) is not None, (
            "取消后重新发起未进入 H5 登录页(疑误锁或弹层残留)")
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("QQ音乐", timeout=10) is not None, (
            "重入退出后未回到平台页")
        self.userA.assert_no_auth_error()
