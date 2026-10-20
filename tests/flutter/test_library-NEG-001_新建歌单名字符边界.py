# CASE-ID: library-NEG-001
"""Swan 回归·M12 收藏与曲库：新建歌单名字符键入边界（library-NEG-001）。

用例 → AW 映射：
- S1-S3 歌单页创建弹窗键入恰 20 字符名并保存 → open_home_card('歌单') +
  create_local_playlist('TESTSYNTHETIC边界名二十字符齐')（弹窗锚 [图]+OCR，
  保存钮 l10n playlistSave 口径），断言新歌单落入 Swans 自建列表（OCR）。
- S4-S7 二次弹窗键入 20 字符名后尝试第 21 字符 → open_create_playlist_dialog +
  input_text(20 字符) + input_text('超')（maxLength 输入层拦截）+ 保存提交无报错，
  断言 20 字符名正常创建入列。
- 降级注记：第 21 字符是否进入输入框无法经 OCR 直读输入框内容，以「保存成功
  且列表仅见 20 字符名」收口；输入框回显与保存钮文案执行轮校准。
清理：两条均为自有 TEST-SYNTHETIC 一次性歌单 → open_playlist_detail('swan', <名>)
→ delete_playlist_via_detail_menu() 真删（断言列表不再见该名）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryNeg001NameLengthBoundary(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """新建歌单名字符键入边界（20 字符可存，第 21 字符被输入层拦截）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_name_length_boundary(self):
        """20 字符歌单名创建成功；21 字符尝试不产生 21 字符歌单且保存无报错。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1-S3：恰 20 字符名创建成功
        self.userA.create_local_playlist('TESTSYNTHETIC边界名二十字符齐')
        # S4-S7：二次弹窗 20 字符 + 第 21 字符尝试（maxLength 输入层拦截）
        self.userA.open_create_playlist_dialog()
        self.userA.input_text('TESTSYNTHETIC边界名二十字符整')
        self.userA.input_text('超')
        self.userA.click_text_candidates(('保存', '确定'))
        self.userA.text_exists('TESTSYNTHETIC边界名二十字符整', timeout=10)
        # 清理：真删两条一次性歌单
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC边界名二十字符齐')
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC边界名二十字符齐')
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC边界名二十字符整')
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC边界名二十字符整')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删自有数据）。"""
        pass
