# CASE-ID: music-POS-006
"""Swan 回归·M07 Apple Music:AM 主页可达·独立主页型(music-POS-006)。

步骤→AW 映射:
  1. 底部导航进平台入口页 → go_bottom_tab('平台')(根节点锚)
  2. 平台列表点 Apple Music 条目 → open_platform_home('apple')(已授权态
     闸门+行体点击,主页顶栏「Apple Music」[OCR] 到达锚+列表加载稳态);
     AM 为服务端 isShow⊕本机 token 双源态,未授权点条目触发授权链——按
     YAML SKIP-AUTH 闸门自适配跳过,改由授权族用例覆盖
  3. 内容渲染无异常且未误弹授权弹层 → assert_no_auth_error()

cleanup: 无(只读冒烟);框架每用例冷启动。
B 标定说明:AM 主页内容面文案未截模板,到达锚用顶栏「Apple Music」;主页
内容锚真机补截后可加严(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos006AmHomeReachable(BaseTest):
    """Apple Music 独立主页型可达,内容渲染无异常,未误弹授权弹层。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_am_home_reachable(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_platform_home("apple")
        self.userA.assert_no_auth_error()
