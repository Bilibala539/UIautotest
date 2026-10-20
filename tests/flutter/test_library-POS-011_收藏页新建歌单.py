# CASE-ID: library-POS-011
"""Swan 回归·M12 收藏与曲库：我的收藏新建歌单闭环（library-POS-011）。

用例 → AW 映射：
- S1 我的收藏页新建歌单入口：open_my_collects_page → open_collect_create_dialog
  （添加歌单按钮 [图] → 弹窗锚）。
- S2-S3 空名直接提交判空：click_any_text(('保存', '确定')) → 断言弹窗驻留
  （判空拒绝，宽口径 不能为空/请输入/保存钮仍在）。
- S4-S5 键入歌单名保存入库：input_text('TESTSYNTHETIC-M12-MC-01') → 保存 →
  text_exists(<名>)（收藏页列表可见）。
- S6-S7 清理复用歌单删除路径：删除路径同 library-POS-029 →
  open_playlist_detail('swan', <名>) → delete_playlist_via_detail_menu() 真删。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos011CollectCreatePlaylistLoop(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """我的收藏新建歌单闭环：空名判空拒收，命名保存入库可删除。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_collect_create_playlist_loop(self):
        """收藏页入口新建歌单：空名拒收，命名创建成功并真删还原。"""
        self.userA.ensure_logged_in_on_home()
        # S1：收藏页新建入口
        self.userA.open_my_collects_page()
        self.userA.open_collect_create_dialog()
        # S2-S3：空名提交判空拒绝（弹窗驻留）
        self.userA.click_text_candidates(('保存', '确定'))
        assert self.userA.probe_any_text(
            ('不能为空', '请输入', '保存'), timeout_each=3) is not None, (
            "空名提交后弹窗关闭（判空未生效）")
        # S4-S5：命名保存入库
        self.userA.input_text('TESTSYNTHETIC-M12-MC-01')
        self.userA.click_text_candidates(('保存', '确定'))
        self.userA.text_exists('TESTSYNTHETIC-M12-MC-01', timeout=10)
        # S6-S7：清理（删除路径同 POS-029）
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-MC-01')
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-MC-01')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删一次性歌单）。"""
        pass
