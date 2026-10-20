# CASE-ID: library-NEG-021
"""Swan 回归·M12 收藏与曲库：空态按钮分型矩阵（library-NEG-021，ADD1 复审改判 B 转，部分转换）。

用例 → AW 映射：
- S1 我的收藏空态（零数据账号）：共享账号收藏数据非空，空态不可构造
  ——按 YAML 自身口径登记 SKIP-BRANCH 分支，不纳入本自动转写。
- S2 聚合段空态带新建入口：聚合段进入 + 页驻留锚断言（已加载全部）；
  段内空/非空由账号数据态决定，新建入口可见性登记执行轮校准
  （template_needs）。
- S3 未授权平台段空态无按钮（酷狗/Apple Music，天然空态可替代）：
  click_text 进段 → 断言顶栏加号 [图] 不渲染 + 授权引导文案命中。
- S4 顶栏加号显隐矩阵：Swans 段（有新建能力）加号 [图] 可见 ↔ 未授权
  段加号 [图] 不渲染，一正一反成对断言。
降级注记：各平台空态专属文案未核准（执行轮采样校准）；段切换后的
按钮态依赖加号是否平台级渲染，若实现为全局常驻则 S3 反向断言失败，
即为执行轮校准发现。
清理：纯浏览与段切换，无数据变更。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin
from image.image_name_mapping import SWAN_PLAYLIST_CREATE_BTN, SWAN_PLAYLIST_TAB_SWAN


class TestLibraryNeg021EmptyStateButtonMatrix(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """空态按钮分型矩阵：未授权段空态无新建按钮，Swans 段加号可见。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_empty_state_button_matrix(self):
        """未授权段空态无按钮且带授权引导；Swans 段加号可见。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S4 正向：Swans 段（有新建能力）顶栏加号可见
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=10)
        assert self.userA.find_image(SWAN_PLAYLIST_CREATE_BTN, timeout=5) is not None, (
            "Swans 段顶栏加号 [图] 未渲染（S4 显隐矩阵正向失守）")
        # S2：聚合段进入 + 页驻留（空态新建入口分型登记校准）
        self.userA.open_composite_segment()
        self.userA.assert_any_text(('已加载全部', '聚合'), timeout=8)
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)
        # S3：未授权平台段空态——加号不渲染 + 授权引导命中
        for seg in ('酷狗', 'Apple Music'):
            if self.userA.find_text_by_ocr(seg, timeout=3) is None:
                continue
            self.userA.click_text(seg, timeout=5)
            assert self.userA.find_image(SWAN_PLAYLIST_CREATE_BTN, timeout=3) is None, (
                f"{seg} 段（空态）顶栏加号仍渲染（S3/S4 反向失守）")
            assert self.userA.probe_any_text(
                ('去授权', '立即授权', '授权'), timeout_each=3) is not None, (
                f"{seg} 段空态未见授权引导文案（分型表失配）")
            self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览与段切换）。"""
        pass
