# CASE-ID: search-POS-004
"""Swan 回归·搜索：音乐 Tab 搜索入口进搜索输入页(search-POS-004)。

步骤→AW 映射（用例主体即入口本身，按 YAML 忠实转换）：
- 切音乐 Tab → go_top_tab('音乐')（顶 Tab 选中态锚断言）
- 点音乐 Tab 搜索卡进输入页 → open_search_input_page(
  bar_image=SWAN_HOME_MUSIC_SEARCH_BAR, ocr_fallback='跨平台搜索音乐')
  （mixin 内含：条图优先/OCR 兜底 + 授权通知弹层处置 + 输入页 hint 到位
  断言）

⚠️ 漂移注记：YAML 基于 b34 旧构建（音乐 Tab=搜索卡）；swan.py verify R2
拍板新构建"音乐 Tab 已改歌单流、搜索条回归推荐 Tab"。本用例按 YAML 转换，
若构建确已漂移，入口探测处失败即漂移证据——执行轮按真机现状标定。
cleanup：无用例私有清理（结束态为搜索输入页，随冷启动复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_MUSIC_SEARCH_BAR
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestMusicTabSearchEntry(SwanRP03Mixin, BaseTest):
    """音乐 Tab 搜索卡进入搜索输入页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_music_tab_search_entry(self):
        """音乐 Tab → 搜索卡 → 输入页 hint 到位。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('音乐')
        self.userA.open_search_input_page(
            bar_image=SWAN_HOME_MUSIC_SEARCH_BAR,
            ocr_fallback='跨平台搜索音乐')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索输入页
