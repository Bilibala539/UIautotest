# CASE-ID: library-POS-030
"""Swan 回归·M12 收藏与曲库：本地歌单改名（library-POS-030）。

用例 → AW 映射：
- S1 前置一次性歌单：create_local_playlist('TESTSYNTHETIC-M12-REN-00')。
- S2-S4 改名：open_playlist_detail('swan', <名>) → rename_playlist_via_menu
  （更多按钮 [图] → 改名/重命名 → 清空重输 → 保存 → 新名回显断言）。
- S5 列表同步：press_back → text_exists(新名)。
- S6 清理改回：open_playlist_detail(新名) → rename_playlist_via_menu(原名)。
- 降级注记：本地歌单改名入口未锚定（详情更多菜单族死代码候选，卡片坑 1），
  按（改名/重命名）宽口径，执行轮探锚校准（template_needs 登记）。
清理：一次性歌单真删 → delete_playlist_via_detail_menu。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos030RenameLocalPlaylist(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """本地歌单改名：菜单改名生效，详情与列表同步新名，可改回删除。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_rename_local_playlist(self):
        """本地歌单改名闭环：新名回显、列表同步、改回还原并真删。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：前置一次性歌单
        self.userA.create_local_playlist('TESTSYNTHETIC-M12-REN-00')
        # S2-S4：详情菜单改名
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-REN-00')
        self.userA.rename_playlist_via_menu('TESTSYNTHETIC-M12-REN-01')
        # S5：列表同步
        self.userA.press_back()
        self.userA.text_exists('TESTSYNTHETIC-M12-REN-01', timeout=10)
        # S6：清理改回
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-REN-01')
        self.userA.rename_playlist_via_menu('TESTSYNTHETIC-M12-REN-00')
        # 清理：真删
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-REN-00')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性歌单）。"""
        pass
