# CASE-ID: library-POS-015
"""Swan 回归·M12 收藏与曲库：歌单页三段 Tab 切换（library-POS-015）。

用例 → AW 映射：
- S1 三段 Tab 齐备：open_home_card('歌单') → assert_any_text(('创建', '收藏',
  '关联'))。
- S2-S3 收藏段/关联段切换：click_text('收藏') / click_text('关联')，各段列表
  渲染断言 assert_any_text(('首歌', '暂无', '授权', '空'))（内容行/空态/授权
  提示宽口径——第三方段内容依赖账号授权态）。
- S4 回创建段：click_text('创建')，列表渲染复核。
清理：纯浏览切换，无数据变更，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos015SegmentSwitching(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """三段 Tab 切换：各段可达且列表区渲染，回默认段无残留。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_segment_switching(self):
        """创建/收藏/关联三段依次切换，各段列表区渲染，回创建段正常。"""
        self.userA.ensure_logged_in_on_home()
        # S1：三段齐备
        self.userA.open_home_card('歌单')
        self.userA.assert_any_text(('创建', '收藏', '关联'), timeout=10)
        # S2：收藏段
        self.userA.click_text('收藏', timeout=5)
        self.userA.assert_any_text(('首歌', '暂无', '授权', '空'), timeout=8)
        # S3：关联段
        self.userA.click_text('关联', timeout=5)
        self.userA.assert_any_text(('首歌', '暂无', '授权', '空'), timeout=8)
        # S4：回创建段
        self.userA.click_text('创建', timeout=5)
        self.userA.assert_any_text(('首歌', '暂无', '已加载'), timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览切换）。"""
        pass
