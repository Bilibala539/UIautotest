# CASE-ID: library-POS-017
"""Swan 回归·M12 收藏与曲库：空态按钮分型与加号显隐（library-POS-017，ADD1 复审改判 B 转，坑 27）。

用例 → AW 映射：
- S1 Swans 段（有数据、有新建能力）：顶栏加号 [图] 渲染 + 页骨架锚
  （已加载全部）命中。
- S2 未授权平台段（酷狗/Apple Music，天然空态可替代，YAML 前置口径）：
  click_text 进段 → 空态无新建入口（加号 [图] 不渲染）+ 授权引导文案
  命中（空态分型=授权引导，非新建入口）。
- S3 分型表语义断言：同一顶栏位在有新建能力平台渲染加号、在未授权
  平台让位于授权引导——S1/S2 成对承载。
降级注记：空态专属文案（如「暂无歌单」）未核准，执行轮采样登记
template_needs；我的收藏/聚合空态分支依赖零数据账号（共享账号非空），
按 SKIP-BRANCH 口径不纳入本转写。
清理：纯浏览与段切换，无数据变更。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin
from image.image_name_mapping import SWAN_PLAYLIST_CREATE_BTN, SWAN_PLAYLIST_TAB_SWAN


class TestLibraryPos017EmptyStateButtonType(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """空态按钮分型与加号显隐：有新建能力见加号，未授权空态见授权引导。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_empty_state_button_type_and_plus_visibility(self):
        """Swans 段加号可见；未授权段空态无加号且授权引导命中。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：Swans 段——加号渲染 + 页骨架
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=10)
        self.userA.assert_any_text(('已加载全部', '首歌', '聚合'), timeout=8)
        assert self.userA.find_image(SWAN_PLAYLIST_CREATE_BTN, timeout=5) is not None, (
            "Swans 段顶栏加号 [图] 未渲染")
        # S2-S3：未授权平台段空态——无新建入口，授权引导命中
        seg_seen = False
        for seg in ('酷狗', 'Apple Music'):
            if self.userA.find_text_by_ocr(seg, timeout=3) is None:
                continue
            seg_seen = True
            self.userA.click_text(seg, timeout=5)
            assert self.userA.find_image(SWAN_PLAYLIST_CREATE_BTN, timeout=3) is None, (
                f"{seg} 段（空态）仍渲染新建加号（分型失守）")
            assert self.userA.probe_any_text(
                ('去授权', '立即授权', '授权'), timeout_each=3) is not None, (
                f"{seg} 段空态未见授权引导（分型表失配）")
            self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)
        assert seg_seen, "歌单页未见任何未授权平台 Tab（酷狗/Apple Music），前置不满足"

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览与段切换）。"""
        pass
