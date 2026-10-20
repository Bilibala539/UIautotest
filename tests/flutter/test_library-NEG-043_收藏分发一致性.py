# CASE-ID: library-NEG-043
"""Swan 回归·M12 收藏与曲库：收藏变更分发跨页一致性（library-NEG-043，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射（5s 收敛窗口以 OCR 探测等待承载）：
- 前置：自建基线本地歌单 + 一个聚合歌单（TESTSYN 一次性数据）。
- S1+S3 收藏变更循环与快速连续变更：open_playlist_detail 落基线歌单
  详情 → favorite_playlist('swan','toggle') 连续 6 次（S1 收藏→取消→
  收藏 3 次 + S3 快速连续 3 次；方法内逐次断言图标两态翻转 [图]；
  6 次偶数翻转终态回原态，收藏数据零残留）。
- S2 聚合改名分发：open_composite_detail → composite_rename——改名后
  详情头新名命中（方法内断言）。
- S4 杀进程冷启动重进两页：relaunch_app → 歌单页见聚合新名 → 我的
  收藏页锚（我的音乐分组行 [图]）命中（跨页一致性复核）。
降级注记：5s 防抖收敛的毫秒级时序不作硬断言，以变更后逐次 OCR 探测
（每次探测即一次收敛等待）承载；本地歌单详情若不渲染收藏星标，则
favorite_playlist 在执行轮失败——即星标数据面校准点（template_needs
登记）。
清理：聚合与本地基线一次性数据确认删除（收藏态 6 次翻转零残留）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin

LOCAL = 'TESTSYN分发基准L'
AGG = 'TESTSYN分发聚合'
AGG_R2 = 'TESTSYN分发聚合R2'


class TestLibraryNeg043FavoriteDispatchConsistency(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """收藏变更分发跨页一致性：星标翻转与聚合改名后冷启动两页一致。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_favorite_dispatch_cross_page_consistency(self):
        """星标连续翻转回原态；聚合改名冷启动后歌单页与收藏页一致。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # 前置：基线本地歌单 + 聚合歌单
        self.userA.create_local_playlist(LOCAL)
        self.userA.create_composite_playlist(AGG)
        # S1+S3：收藏变更循环 3 次 + 快速连续变更 3 次（偶数次回原态）
        self.userA.press_back()
        self.userA.open_playlist_detail('swan', LOCAL)
        for _ in range(6):
            self.userA.favorite_playlist('swan', 'toggle')
        # S2：聚合改名（分发源变更）
        self.userA.press_back()
        self.userA.open_composite_detail(AGG)
        self.userA.composite_rename(AGG_R2)
        # S4：杀进程冷启动 → 重进歌单页与我的收藏页复核一致性
        self.userA.relaunch_app(self.userA.package)
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        self.userA.open_composite_segment()
        self.userA.assert_any_text((AGG_R2,), timeout=10)
        self.userA.press_back()
        self.userA.open_my_collects_page()
        # 清理：回首页后删聚合（编辑弹层确认删除）与本地基线（详情菜单删除）
        self.userA.relaunch_app(self.userA.package)
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        self.userA.open_composite_detail(AGG_R2)
        self.userA.composite_delete_to_confirm()
        self.userA.composite_delete_confirm(AGG_R2)
        self.userA.press_back()
        self.userA.open_home_card('歌单')
        self.userA.open_playlist_detail('swan', LOCAL)
        self.userA.delete_playlist_via_detail_menu(LOCAL)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（用例体内已含确定性清理）。"""
        pass
