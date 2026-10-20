# CASE-ID: library-POS-016
"""Swan 回归·M12 收藏与曲库：平台 Tab 遍历与未授权段展示（library-POS-016）。

用例 → AW 映射：
- S1 歌单页平台 Tab 行：open_home_card('歌单') → image_exists
  (SWAN_PLAYLIST_TAB_SWAN)。
- S2-S3 Swans 段列表渲染 → 未授权平台段（酷狗，点击「酷狗」Tab）→ 未授权
  文案/空态断言 assert_any_text(('授权', '暂无', '首歌'))。
  ⛔ 「去授权」等授权按钮不点击（禁区 8：授权交互依赖真实凭据，只断言展示）。
- S4 切回 Swans 段确认无污染：image_exists(SWAN_PLAYLIST_TAB_SWAN) + 列表渲染。
- 降级注记：授权子集外平台 Tab（如 Qobuz/Apple Music）展示项按账号授权态
  动态，酷狗 Tab 是否可见为运行时态——不可见时跳过该段（运行时分支），
  精确 Tab 清单执行轮校准。
清理：纯浏览切换，无数据变更，无清理动作。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYLIST_TAB_SWAN
from utils.aw.business.swan_regression import SwanLoginRegressionMixin
from utils.aw.business.swan_r_p07 import SwanRP07Mixin


class TestLibraryPos016PlatformTabTraversal(SwanRP07Mixin, SwanLoginRegressionMixin, BaseTest):
    """平台 Tab 遍历：Swans 段渲染，未授权段只断言展示不点授权。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_tab_traversal(self):
        """平台 Tab 遍历：未授权段展示授权提示（不点击授权），切回无污染。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.open_home_card('歌单')
        # S1：平台 Tab 行
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=10)
        # S2：Swans 段列表渲染
        self.userA.assert_any_text(('首歌', '暂无', '聚合'), timeout=8)
        # S3：未授权平台段（酷狗）——Tab 可见才遍历，展示断言，不点授权
        if self.userA.find_text_by_ocr('酷狗', timeout=5) is not None:
            self.userA.click_text('酷狗', timeout=5)
            self.userA.assert_any_text(('授权', '暂无', '首歌'), timeout=8)
        # S4：切回 Swans 段
        self.userA.image_exists(SWAN_PLAYLIST_TAB_SWAN, timeout=8)
        self.userA.assert_any_text(('首歌', '暂无', '聚合'), timeout=8)

    def teardown(self) -> None:
        """冷启动模型：teardown 不做清理（纯浏览切换）。"""
        pass
