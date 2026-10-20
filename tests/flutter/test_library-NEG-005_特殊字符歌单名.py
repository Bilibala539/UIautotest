# CASE-ID: library-NEG-005
"""Swan 回归·M12 收藏与曲库：特殊字符歌单名原样渲染（library-NEG-005）。

用例 → AW 映射：
- S1-S2 脚本注入串建单：open_home_card('歌单') → open_create_playlist_dialog →
  input_text('TEST<script>alert(1)</script>SYN') → 保存 → 字面入库。
  断言（OCR contains 特征片段）：text_exists('script')——<>/标点 OCR 识别
  不稳，取片段 contains 收口。
- S3 SQL 注入串建单：input_text("TEST'; DROP TABLE favorite--SYN") → 保存 →
  text_exists('DROP TABLE')。
- 降级注记：换行符键入（S1 数据第 3 分支）adb input_text 不可控不转；改名
  回显段依赖未锚定改名入口，改名路径已由 library-POS-030 覆盖。
清理：两条一次性歌单 → open_playlist_detail('swan', <特征片段> 行包含匹配)
→ delete_playlist_via_detail_menu() 真删。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryNeg005SpecialCharName(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """特殊字符歌单名原样入库渲染（脚本注入串/SQL 注入串无转义异常）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_special_char_name_stored(self):
        """特殊字符名可创建且原样显示，删除路径不因特殊字符异常。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1-S2：脚本注入串
        self.userA.open_create_playlist_dialog()
        self.userA.input_text('TEST<script>alert(1)</script>SYN')
        self.userA.click_text_candidates(('保存', '确定'))
        self.userA.text_exists('script', timeout=10)
        # S3：SQL 注入串
        self.userA.open_create_playlist_dialog()
        self.userA.input_text("TEST'; DROP TABLE favorite--SYN")
        self.userA.click_text_candidates(('保存', '确定'))
        self.userA.text_exists('DROP TABLE', timeout=10)
        # 清理：按行包含匹配定位真删
        self.userA.open_playlist_detail('swan', 'script')
        self.userA.delete_playlist_via_detail_menu('script')
        self.userA.open_playlist_detail('swan', 'DROP TABLE')
        self.userA.delete_playlist_via_detail_menu('DROP TABLE')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删自有数据）。"""
        pass
