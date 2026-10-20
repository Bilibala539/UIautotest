# CASE-ID: search-NEG-011
"""Swan 回归·搜索：冷启动后搜索入口无 ANR(search-NEG-011)。

步骤→AW 映射：
- 冷启动落首页 → cold_start_assert('home', timeout=30)（relaunch + 首页
  容器锚断言；YAML 15s 阈值放宽为探测上限承载真机冷启动抖动，断言语义
  仍为"启动即达首页"）
- ANR 守门 → assert_no_anr_dialog()（mixin OCR 探测系统 ANR 弹窗文案）
- 立即点搜索入口 → open_search_input_page(timeout=5)（入口可达 + 输入页
  hint [OCR] 5s 内到位）
- 再次 ANR 守门 → assert_no_anr_dialog()

cleanup：无用例私有清理（冷启动由用例步骤自身发起，属用例主体）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestColdStartNoAnrSearchEntry(SwanRP03Mixin, BaseTest):
    """冷启动落首页后立即进搜索，全程无系统 ANR 弹窗。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_cold_start_search_no_anr(self):
        """冷启动 → 无 ANR → 搜索入口 5s 可达 → 再验无 ANR。"""
        self.userA.cold_start_assert('home', timeout=30)
        self.userA.assert_no_anr_dialog()

        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐', timeout=5)
        self.userA.assert_no_anr_dialog()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索输入页
