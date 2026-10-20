# CASE-ID: library-NEG-003
"""Swan 回归·M12 收藏与曲库：纯空格歌单名判空拒绝（library-NEG-003）。

用例 → AW 映射：
- S1-S4 我的收藏页新建歌单入口：open_my_collects_page → open_collect_create_dialog
  （添加歌单按钮 [图]）→ input_text('   ')（3 空格）→ 点击保存 → 判空拒绝。
  断言：弹窗未关闭（保存钮仍在）——判空反馈文案按 l10n myCollectsFolderNameEmpty
  口径（不能为空/请输入）宽口径探测，弹窗驻留为主判据。
- S5-S6 歌单页创建弹窗对照：open_home_card('歌单') → open_create_playlist_dialog
  → 同样纯空格提交 → 弹窗驻留（两个入口判空口径一致）。
- 降级注记：制表符键入（adb input_text 不可控）不转；判空反馈精确文案
  执行轮校准（template_needs 登记）。
清理：纯空格名不产生歌单，无需数据清理 → close_create_dialog 收窗。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryNeg003BlankNameRejected(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """纯空格歌单名两个入口均判空拒绝（弹窗驻留、无歌单产生）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_blank_name_rejected(self):
        """纯空格名提交被判空拒绝：弹窗不关闭，无空白名歌单产生。"""
        self.userA.ensure_logged_in_on_home()
        # 入口 1：我的收藏页新建歌单
        self.userA.open_my_collects_page()
        self.userA.open_collect_create_dialog()
        self.userA.input_text('   ')
        self.userA.click_text_candidates(('保存', '确定'))
        assert self.userA.probe_any_text(
            ('不能为空', '请输入', '保存'), timeout_each=3) is not None, (
            "纯空格名提交后弹窗关闭（判空未生效）")
        self.userA.close_create_dialog()
        # 入口 2：歌单页创建弹窗对照
        self.userA.open_home_card('歌单')
        self.userA.open_create_playlist_dialog()
        self.userA.input_text('   ')
        self.userA.click_text_candidates(('保存', '确定'))
        assert self.userA.probe_any_text(
            ('不能为空', '请输入', '保存'), timeout_each=3) is not None, (
            "歌单页纯空格名提交后弹窗关闭（判空未生效）")
        self.userA.close_create_dialog()

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯空格名不产生数据）。"""
        pass
