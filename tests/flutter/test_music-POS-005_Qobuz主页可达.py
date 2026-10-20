# CASE-ID: music-POS-005
"""Swan 回归·M07 Qobuz:Qobuz 主页可达·独立主页型(music-POS-005)。

步骤→AW 映射:
  1. 底部导航进平台入口页 → go_bottom_tab('平台')(根节点锚)
  2. 平台列表点 Qobuz 条目 → open_platform_home('qobuz')(已授权态闸门+行体
     点击,主页顶栏「Qobuz」[OCR] 到达锚+列表加载稳态);未授权行体点击无
     反应,按 YAML SKIP-NO-ITEM/SKIP-AUTH 闸门自适配跳过(授权链路由授权族
     用例覆盖)
  3. 内容渲染无异常 → assert_no_auth_error()(未误弹授权弹层,无白屏断言
     以到达锚+稳态等待承载)

cleanup: 无(只读冒烟);框架每用例冷启动。
B 标定说明:Qobuz 主页内容面(推荐位/榜单区文案)未截模板,到达锚用顶栏
「Qobuz」;主页内容锚真机补截后可加严(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos005QobuzHomeReachable(BaseTest):
    """Qobuz 独立主页型可达,内容渲染无异常,未误弹授权弹层。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_home_reachable(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        self.userA.open_platform_home("qobuz")
        self.userA.assert_no_auth_error()
