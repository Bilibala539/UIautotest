# CASE-ID: library-POS-034
"""Swan 回归·M12 收藏与曲库：统一音乐库页内 Tab 切换（library-POS-034，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射（前置：统一音乐库内 ≥2 个 Tab 有数据，缺数据 Tab 按
YAML 口径标 SKIP-DATA）：
- S1 打开统一音乐库：open_home_card('我喜欢') → 锚（播放全部 [图] +
  宝藏音乐口号）命中。
- S2 页内 Tab 遍历切换：visit_mylike_page_tabs——播放全部按钮 [图]
  上缘条带 OCR 短文本候选逐个探测点击（Tab 文案不写死，未锚定登记
  template_needs）；候选 <2 时按 SKIP-DATA 口径运行时 skip。
- S3 返回原 Tab 复核 keep-alive：重击首个 Tab 文案 → 播放全部 [图]
  锚复现（列表态保持）。
降级注记：keep-alive 以锚复现承载，不作列表滚动位置级断言；Tab 条
带模板（同播放历史 SWAN_HISTORY_TABBAR 族）待执行轮截取转正。
清理：纯浏览切换，无数据变更。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin
from image.image_name_mapping import SWAN_FAVORITE_PLAY_ALL


class TestLibraryPos034MyLikePageTabSwitch(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """统一音乐库页内 Tab 切换：遍历切换后返回原 Tab，锚复现。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_mylike_page_tab_switch(self):
        """页内 Tab 遍历切换（≥2 个），返回原 Tab 后播放全部锚复现。"""
        self.userA.ensure_logged_in_on_home()
        # S1：统一音乐库（我喜欢页）
        self.userA.open_home_card('我喜欢')
        self.userA.image_exists(SWAN_FAVORITE_PLAY_ALL, timeout=10)
        self.userA.text_exists('宝藏音乐，随心收藏', timeout=8)
        # S2：页内 Tab 遍历切换（Tab 文案不写死）
        tabs = self.userA.visit_mylike_page_tabs()
        if len(tabs) < 2:
            pytest.skip("统一音乐库页内 Tab 候选不足 2 个（数据/布局态），"
                        "按 YAML 口径 SKIP-DATA 转执行轮校准")
        # S3：返回原 Tab，keep-alive 锚复现
        self.userA.click_text(tabs[0], timeout=5)
        self.userA.image_exists(SWAN_FAVORITE_PLAY_ALL, timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览切换）。"""
        pass
