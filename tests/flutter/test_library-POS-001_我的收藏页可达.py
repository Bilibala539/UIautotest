# CASE-ID: library-POS-001
"""Swan 回归·M12 收藏与曲库：我的收藏页可达与分区浏览（library-POS-001）。

用例 → AW 映射：
- S1-S2 我的 Tab → 我的收藏行 → 收藏页：open_my_collects_page（我的 Tab [图] +
  我的收藏行 [图] + 我的音乐分组行 [图] 页锚）。
- S3 分区列表渲染：assert_any_text(('我的音乐', '我的家庭'))（OCR 宽口径，
  分区齐备性）。
- S4 退出收藏页：press_back 回我的页。
清理：纯浏览用例，无数据变更，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos001MyCollectsReachable(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """我的收藏页可达：入口命中、分区渲染、可退出。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_my_collects_reachable(self):
        """我的收藏入口可达，收藏分区渲染，返回后离开收藏页。"""
        self.userA.ensure_logged_in_on_home()
        # S1-S2：进入我的收藏页
        self.userA.open_my_collects_page()
        # S3：分区列表渲染
        self.userA.assert_any_text(('我的音乐', '我的家庭'), timeout=8)
        # S4：退出
        self.userA.press_back()

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览无数据变更）。"""
        pass
