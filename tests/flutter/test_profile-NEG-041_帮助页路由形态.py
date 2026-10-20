# CASE-ID: profile-NEG-041
"""Swan 回归·M13 个人中心：帮助页路由形态（profile-NEG-041）。

用例 → AW 映射（C 级简化转换）：
- 「帮助与反馈」行进入帮助页（行需滚动脱离播放条遮挡 → open_me_row 内建滚动）
- 入口行渲染断言：使用说明/常见问题（OCR 文案锚）
- YAML 路由-only 考古段（原生路由表静态判定）→ 执行注记，自动化面为页面可达+行渲染
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg041HelpPageRouteShape(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_help_page_route_shape(self) -> None:
        self.userA.open_me_page()
        self.userA.open_help_page()
        # 入口行渲染
        self.userA.text_exists("使用说明", timeout=5)
        self.userA.text_exists("常见问题", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
