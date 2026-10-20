# CASE-ID: library-POS-008
"""Swan 回归·M12 收藏与曲库：播放历史页可达与页骨架（library-POS-008）。

用例 → AW 映射：
- S1 首页歌单卡「最近播放」进入：open_home_card('最近播放')。
- S2 页骨架：顶栏 [图]（SWAN_HISTORY_TOPBAR）+ 分类 Tab 条 [图]
  （SWAN_HISTORY_TABBAR）。
- S3 分类 Tab 文案渲染：assert_any_text(('歌曲', '歌单', '专辑', '播客'))
  （OCR 宽口径）。
清理：纯浏览用例，无数据变更，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HISTORY_TABBAR, SWAN_HISTORY_TOPBAR
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos008PlayHistoryReachable(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """播放历史页可达：顶栏/Tab 条锚命中，分类 Tab 文案渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_play_history_reachable(self):
        """播放历史页可达：顶栏与分类 Tab 条渲染，分类文案可见。"""
        self.userA.ensure_logged_in_on_home()
        # S1：进入播放历史
        self.userA.open_home_card('最近播放')
        # S2：页骨架
        self.userA.image_exists(SWAN_HISTORY_TOPBAR, timeout=15)
        self.userA.image_exists(SWAN_HISTORY_TABBAR, timeout=10)
        # S3：分类 Tab 文案
        self.userA.assert_any_text(('歌曲', '歌单', '专辑', '播客'), timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览无数据变更）。"""
        pass
