# CASE-ID: library-POS-006
"""Swan 回归·M12 收藏与曲库：统一音乐库（我喜欢）可达与骨架（library-POS-006）。

用例 → AW 映射：
- S1-S2 首页歌单卡「我喜欢」进入统一音乐库：open_home_card('我喜欢')，页锚
  「宝藏音乐，随心收藏」（我喜欢页特有判据，OCR）。
- S3 页骨架：播放全部入口 [图]（SWAN_FAVORITE_PLAY_ALL）+ 多选/更多入口
  （OCR 宽口径探测）。
清理：纯浏览用例，无数据变更，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_FAVORITE_PLAY_ALL
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos006UnifiedLibraryReachable(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """统一音乐库（我喜欢）可达：特有判据文案与页骨架锚命中。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_unified_library_reachable(self):
        """我喜欢页可达：特有判据文案命中，播放全部与多选入口渲染。"""
        self.userA.ensure_logged_in_on_home()
        # S1-S2：进入统一音乐库
        self.userA.open_home_card('我喜欢')
        self.userA.text_exists('宝藏音乐，随心收藏', timeout=15)
        # S3：页骨架
        self.userA.image_exists(SWAN_FAVORITE_PLAY_ALL, timeout=10)
        assert self.userA.probe_any_text(('多选', '更多'), timeout_each=3) is not None, (
            "页骨架多选/更多入口未命中")

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览无数据变更）。"""
        pass
