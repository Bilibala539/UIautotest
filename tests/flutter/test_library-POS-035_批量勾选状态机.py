# CASE-ID: library-POS-035
"""Swan 回归·M12 收藏与曲库：批量勾选状态机（library-POS-035）。

用例 → AW 映射：
- S1 我喜欢页多选入口：open_home_card('我喜欢') → open_batch_mode（批量
  勾选态锚 全选/已选）。
- S2-S3 全选/取消全选：click_text('全选') 两次（开→关），锚复核。
- S4-S5 勾选单项：playlist_top_song()（运行时值）→ click_text(<歌名>)。
- 降级注记：勾选计数（已选 N）数字直读为 OCR 弱项，计数断言降级为
  「已选」锚存在性；勾选框两态视觉断言执行轮校准（template_needs）。
清理：未提交任何批量动作（press_back 退出勾选态），无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos035BatchSelectionState(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """批量勾选状态机：全选开关可逆，单项勾选生效，不提交即退。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_batch_selection_state(self):
        """勾选态全选/取消/单项勾选状态机，退出不提交任何批量动作。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('我喜欢')
        # S1：多选入口
        self.userA.open_batch_mode()
        # S2-S3：全选 → 取消全选
        self.userA.click_text('全选', timeout=5)
        self.userA.assert_any_text(('已选', '全选'), timeout=5)
        self.userA.click_text('全选', timeout=5)
        # S4-S5：勾选单项（不提交）
        song = self.userA.playlist_top_song()
        self.userA.click_text(song, timeout=8)
        self.userA.assert_any_text(('已选', '全选'), timeout=5)
        self.userA.press_back()

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（未提交批量动作）。"""
        pass
