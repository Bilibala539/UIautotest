# CASE-ID: library-POS-028
"""Swan 回归·M12 收藏与曲库：选择歌单页新建歌单入口（library-POS-028）。

用例 → AW 映射：
- 前置：我喜欢页取最上方歌曲名（playlist_top_song 运行时值）→ 条目动作
  菜单（长按，open_library_song_menu）——菜单形态未探索（卡片坑 1），
  执行轮探锚校准。
- S1 动作菜单 → 添加到歌单 → 选择歌单页：open_select_playlist_page（锚
  新建歌单/选择歌单入口）。
- S2-S5 新建歌单入口：create_playlist_in_select_page('TESTSYNTHETIC-M12-SEL-01')
  （入口 → 命名 → 保存 → 新歌单网格可见）。
- S6 取消本次加歌：press_back ×2（不实际加歌）。
清理：一次性歌单 → open_playlist_detail('swan', <名>) →
delete_playlist_via_detail_menu() 真删。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos028SelectPageCreateEntry(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """选择歌单页新建入口：动作菜单 → 添加到歌单 → 新建歌单入库可删除。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_select_page_create_entry(self):
        """选择歌单页新建歌单闭环：新建入口可用，取消加歌不落数据。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('我喜欢')
        self.userA.text_exists('宝藏音乐，随心收藏', timeout=15)
        # 前置：最上方歌曲 → 条目动作菜单
        song = self.userA.playlist_top_song()
        self.userA.open_library_song_menu(song)
        # S1：动作菜单 → 添加到歌单 → 选择歌单页
        self.userA.open_select_playlist_page()
        # S2-S5：新建歌单入库
        self.userA.create_playlist_in_select_page('TESTSYNTHETIC-M12-SEL-01')
        # S6：取消本次加歌
        self.userA.press_back()
        self.userA.press_back()
        # 清理：真删一次性歌单
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-SEL-01')
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-SEL-01')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性歌单）。"""
        pass
