# CASE-ID: library-POS-029
"""Swan 回归·M12 收藏与曲库：本地歌单删除主路径（library-POS-029）。

用例 → AW 映射：
- S1 前置一次性歌单：create_local_playlist('TESTSYNTHETIC-M12-DEL-01')。
- S2-S3 删除：open_playlist_detail('swan', <名>) → 更多按钮 [图] →
  「删除歌单/删除」 → 确认（delete_playlist_via_detail_menu）。
- S4 删除后消失：方法内终态断言——歌单页列表不再见该名（OCR contains）。
- 降级注记：详情更多菜单族为死代码候选（卡片坑 1），删除入口文案按
  （删除歌单/删除）宽口径，执行轮探锚校准（template_needs 登记）。
清理：删除本身即用例主体，无额外清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos029DeleteLocalPlaylist(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """本地歌单删除主路径：详情更多菜单删除，删除后列表不再可见。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_delete_local_playlist(self):
        """自建歌单经详情菜单删除，删除后列表不再见该歌单。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：前置一次性歌单
        self.userA.create_local_playlist('TESTSYNTHETIC-M12-DEL-01')
        # S2-S4：详情菜单删除 + 消失断言
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-DEL-01')
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-DEL-01')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（删除即用例主体）。"""
        pass
