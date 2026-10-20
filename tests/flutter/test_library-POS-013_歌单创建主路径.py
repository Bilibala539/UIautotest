# CASE-ID: library-POS-013
"""Swan 回归·M12 收藏与曲库：歌单创建主路径（library-POS-013）。

用例 → AW 映射：
- S1-S2 歌单页打开创建弹窗：open_home_card('歌单') → open_create_playlist_dialog
  （新建按钮 [图] → 弹窗锚）。
- S3-S4 平台与类型默认态：assert_any_text(('Swans', 'SWAN')) + assert_any_text
  (('自建',))（弹窗内平台清单/类型选项 OCR 宽口径）。
- S5-S7 命名保存入库：input_text('TESTSYNTHETIC-M12-PL-01') → 保存 →
  text_exists(<名>)（Swans 自建列表可见）。
清理：一次性歌单 → open_playlist_detail('swan', <名>) →
delete_playlist_via_detail_menu() 真删。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos013CreatePlaylistMainPath(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """歌单创建主路径：弹窗默认态正确，命名保存后落入 Swans 自建列表。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_create_playlist_main_path(self):
        """创建歌单主路径：平台/类型默认态，命名保存入库并真删还原。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1-S2：打开创建弹窗
        self.userA.open_create_playlist_dialog()
        # S3-S4：平台与类型默认态
        self.userA.assert_any_text(('Swans', 'SWAN'), timeout=5)
        self.userA.assert_any_text(('自建',), timeout=5)
        # S5-S7：命名保存入库
        self.userA.input_text('TESTSYNTHETIC-M12-PL-01')
        self.userA.click_text_candidates(('保存', '确定'))
        self.userA.text_exists('TESTSYNTHETIC-M12-PL-01', timeout=10)
        # 清理：真删
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-PL-01')
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-PL-01')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性歌单）。"""
        pass
