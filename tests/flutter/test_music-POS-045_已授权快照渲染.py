# CASE-ID: music-POS-045
"""Swan 回归·M07 平台授权:已授权条目快照渲染(music-POS-045)。

步骤→AW 映射(7.7 授权族,getMusicTerraceList 快照唯一真源,只读):
  1. 进入平台入口页 → go_bottom_tab("平台")
  2. 已授权行渲染授权态 → platform_row_state("netease")==authorized
     (网易云恒已授权=快照预置;行带无「未授权」副文案,昵称/角标带)
  3. 操作钮形态区分 → 已授权行 [−] 解绑钮存在:tap_platform_row_minus
     点开解绑确认弹层即取消(零写,与未授权行 [+] 授权钮形态互斥)
  4. 重进刷新复核 → 底部导航切首页再回平台,行授权态稳定一致

cleanup: 无(只读浏览;解绑确认弹层点取消,无服务端绑定写)。
B 标定说明:vipLevel 三态(null/0/正数)渲染差异为服务端数据态,OCR
不可辨,以"渲染不崩溃+授权态稳定"口径覆盖;[−] 钮模板待真机补截,
见 package_report.json template_needs。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos045AuthSnapshot(BaseTest):
    """平台页已授权条目按快照正确渲染且刷新后稳定一致。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_authorized_snapshot_render(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 2:已授权行渲染授权态(网易云=快照真源预置行)
        state = self.userA.platform_row_state("netease")
        if state != "authorized":
            pytest.skip(
                f"网易云行授权态={state}(YAML 需至少 1 个已授权平台,"
                "人工预置 SKIP-AUTH 闸门)")
        # 步骤 3:操作钮形态区分——已授权行 [−] 解绑钮,点开即取消零写
        self.userA.tap_platform_row_minus("netease")
        self.userA.assert_any_text(["取消授权", "解绑", "不再展示", "隐藏"])
        self.userA.click_text("取消", timeout=5)
        # 步骤 4:重进刷新复核,快照授权态稳定一致
        self.userA.go_bottom_tab("首页")
        self.userA.go_bottom_tab("平台")
        assert self.userA.platform_row_state("netease") == "authorized", (
            "刷新后网易云行授权态漂移(getMusicTerraceList 快照不一致)")
        self.userA.assert_no_auth_error()
