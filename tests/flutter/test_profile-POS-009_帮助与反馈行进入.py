# CASE-ID: profile-POS-009
"""Swan 回归·M13 个人中心：帮助与反馈行进入（profile-POS-009）。

用例 → AW 映射（A- 级）：
- 「帮助与反馈」行进入（行需滚动脱离播放条遮挡）→ open_help_page
- 四入口行渲染：可适配音箱型号/使用说明/用户反馈/常见问题（OCR 文案锚）
- 未读红点为视觉角标（截元素规范禁入模板）→ 数值面执行注记
- back 返回我的页
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfilePos009HelpRowEntry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_help_row_entry(self) -> None:
        self.userA.open_me_page()
        self.userA.open_help_page()
        self.userA.text_exists("可适配音箱型号", timeout=5)
        self.userA.text_exists("使用说明", timeout=5)
        self.userA.text_exists("用户反馈", timeout=5)
        self.userA.text_exists("常见问题", timeout=5)
        self.userA.back_to_me_page()

    def teardown(self) -> None:
        pass
