# CASE-ID: library-POS-003
"""Swan 回归·M12 收藏与曲库：本地歌单详情页进入与分流（library-POS-003）。

用例 → AW 映射：
- S1 歌单页定位本地歌单：open_home_card('歌单')；无目标歌单时先经
  create_local_playlist 自建一条（无则先经创建，一次性数据口径）。
- S2 点歌单行进入详情：open_playlist_detail('swan', 'TESTSYNTHETIC-M12-DET-01')
  （SWAN 分流 + 行包含匹配，落点锚 更多按钮 [图]）。
- S3 详情首屏渲染：image_exists(SWAN_PD_MORE_BTN) + 歌单名回显
  text_exists(<名>)。
清理：一次性歌单 → delete_playlist_via_detail_menu() 真删。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PD_MORE_BTN
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos003LocalPlaylistDetail(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """本地歌单详情页进入：SWAN 分流命中、详情首屏渲染。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_local_playlist_detail(self):
        """本地歌单详情可进入：更多按钮锚命中，歌单名回显一致。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：目标歌单不存在则先自建（一次性数据）
        if self.userA.find_text_by_ocr('TESTSYNTHETIC-M12-DET-01', timeout=5) is None:
            self.userA.create_local_playlist('TESTSYNTHETIC-M12-DET-01')
        # S2：SWAN 分流点行进入详情
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-DET-01')
        # S3：详情首屏渲染
        self.userA.image_exists(SWAN_PD_MORE_BTN, timeout=10)
        self.userA.text_exists('TESTSYNTHETIC-M12-DET-01', timeout=8)
        # 清理：一次性歌单真删
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-DET-01')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性歌单）。"""
        pass
