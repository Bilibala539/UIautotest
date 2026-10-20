# CASE-ID: library-POS-033
"""Swan 回归·M12 收藏与曲库：统一音乐库浏览主路径（library-POS-033）。

用例 → AW 映射：
- S1 我喜欢页加载：open_home_card('我喜欢') → text_exists('宝藏音乐，随心收藏')。
- S2 条目动作菜单：playlist_top_song()（运行时值）→ open_library_song_menu
  （长按 → 菜单锚 添加到歌单/收藏）。
- S3 播放全部入口：image_exists(SWAN_FAVORITE_PLAY_ALL)。
- S4 更多入口：probe_any_text(('更多', '多选'))。
- 降级注记：条目动作菜单形态未探索（卡片坑 1），执行轮探锚校准。
清理：菜单打开即关（press_back，不执行删除类动作），无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_FAVORITE_PLAY_ALL
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos033LibraryBrowseMainPath(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """统一音乐库浏览：列表加载、条目动作菜单可达、播放全部入口渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_library_browse_main_path(self):
        """我喜欢页浏览主路径：动作菜单可拉起可关闭，页骨架入口齐备。"""
        self.userA.ensure_logged_in_on_home()
        # S1：进入统一音乐库
        self.userA.open_home_card('我喜欢')
        self.userA.text_exists('宝藏音乐，随心收藏', timeout=15)
        # S2：条目动作菜单（长按最上方歌曲行）
        song = self.userA.playlist_top_song()
        self.userA.open_library_song_menu(song)
        self.userA.press_back()
        # S3：播放全部入口
        self.userA.image_exists(SWAN_FAVORITE_PLAY_ALL, timeout=8)
        # S4：更多入口
        assert self.userA.probe_any_text(('更多', '多选'), timeout_each=3) is not None, (
            "更多入口未命中")

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（未执行删除类动作）。"""
        pass
