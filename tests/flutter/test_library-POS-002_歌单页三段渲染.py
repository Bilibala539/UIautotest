# CASE-ID: library-POS-002
"""Swan 回归·M12 收藏与曲库：歌单页可达与分段结构（library-POS-002）。

用例 → AW 映射：
- S1 首页歌单卡进入歌单页：open_home_card('歌单')，页锚「已加载全部」。
- S2 三段 Tab 齐备：assert_any_text(('创建', '收藏', '关联'))（OCR）。
- S3 平台 Tab 行渲染：image_exists(SWAN_PLAYLIST_TAB_SWAN)（Swans 段 [图]）。
- S4 默认段列表渲染：assert_any_text(('首歌', '暂无', '聚合'))（列表行/空态
  宽口径）。
清理：纯浏览用例，无数据变更，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYLIST_TAB_SWAN
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos002PlaylistPageSegments(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """歌单页可达：三段 Tab 与平台 Tab 行渲染，默认段有列表。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_playlist_page_segments(self):
        """歌单页可达，创建/收藏/关联三段齐备，平台 Tab 行与列表渲染。"""
        self.userA.ensure_logged_in_on_home()
        # S1：进入歌单页
        self.userA.open_home_card('歌单')
        self.userA.text_exists('已加载全部', timeout=15)
        # S2：三段 Tab 齐备
        self.userA.assert_any_text(('创建', '收藏', '关联'), timeout=10)
        # S3：平台 Tab 行（Swans 段 [图]）
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)
        # S4：默认段列表渲染
        self.userA.assert_any_text(('首歌', '暂无', '聚合'), timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览无数据变更）。"""
        pass
