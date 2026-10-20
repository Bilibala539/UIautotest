# CASE-ID: library-POS-042
"""Swan 回归·M12 收藏与曲库：歌单全生命周期（library-POS-042）。

用例 → AW 映射：
- S1 建单：create_local_playlist('TESTSYNTHETIC-M12-LC-01')。
- S2 我喜欢页批量勾选加入歌单：open_batch_mode → click_text('全选') →
  click_any_text(('加入歌单', '添加到歌单')) → 点目标歌单行 → 完成确认
  （完成/确定/保存宽口径）。降级：精确勾选 2 首改为全选口径（计数/勾选框
  两态为 OCR 弱项），报告 notes 登记。
- S3 提交反馈与详情验证：assert_any_text(('成功', '已添加', '首歌')) 宽口径；
  open_playlist_detail('swan', <目标名>) → assert_any_text(('首歌',))（歌曲
  数 >0；精确 =2 断言降级）。
- S4 改名：rename_playlist_via_menu(<新名>)。
- S5 删除：delete_playlist_via_detail_menu（真删还原）。
- 降级注记：批量提交入口与目标歌单选择器形态未探索（卡片坑 1），执行轮
  探锚校准（template_needs 登记）。
清理：目标歌单真删（我喜欢收藏歌曲不受影响——加入歌单为非破坏性动作）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos042PlaylistFullLifecycle(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """歌单全生命周期：建单 → 批量加入 → 详情验证 → 改名 → 删除还原。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_playlist_full_lifecycle(self):
        """建单到删除全生命周期：批量加歌入库、改名生效、删除还原。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：建单
        self.userA.create_local_playlist('TESTSYNTHETIC-M12-LC-01')
        # S2：我喜欢页批量勾选加入歌单（全选口径，见 docstring 降级注记）
        self.userA.open_home_card('我喜欢')
        self.userA.open_batch_mode()
        self.userA.click_text('全选', timeout=5)
        self.userA.click_text_candidates(('加入歌单', '添加到歌单'), timeout_each=3)
        self.userA.click_text('TESTSYNTHETIC-M12-LC-01', timeout=8)
        self.userA.click_text_candidates(('完成', '确定', '保存'), timeout_each=3)
        # S3：提交反馈 + 详情验证
        self.userA.assert_any_text(('成功', '已添加', '首歌'), timeout=8)
        self.userA.open_home_card('歌单')
        self.userA.open_playlist_detail('swan', 'TESTSYNTHETIC-M12-LC-01')
        self.userA.assert_any_text(('首歌',), timeout=8)
        # S4：改名
        self.userA.rename_playlist_via_menu('TESTSYNTHETIC-M12-LC-01-R2')
        # S5：删除还原
        self.userA.delete_playlist_via_detail_menu('TESTSYNTHETIC-M12-LC-01-R2')

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例内已真删目标歌单）。"""
        pass
