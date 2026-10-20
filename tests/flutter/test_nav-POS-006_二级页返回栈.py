# CASE-ID: nav-POS-006
"""Swan 回归·M03 主框架导航：二级页返回逐层回首页（nav-POS-006）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()
- 二级页①搜索页（/main/search）→ [图] SWAN_HOME_MUSIC_SEARCH_BAR 进页 +
  [图] SWAN_SEARCH_SUBMIT 页锚点 → press_back() → assert_on_home()
- 二级页②我喜欢页（首页卡片推入页）→ open_home_card("我喜欢") 进页 +
  [OCR] 页副标题「宝藏音乐，随心收藏」→ press_back() → assert_on_home()
（返回栈逐层回退以两次独立二级页链路表达；搜索页空白态内容渲染由
SWAN_SEARCH_SUBMIT 锚点覆盖。）
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_HOME_MUSIC_SEARCH_BAR,
    SWAN_SEARCH_SUBMIT,
)


class TestNavPos006SecondaryBackStack(BaseTest):
    """二级页返回逐层回首页（nav-POS-006）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_secondary_pages_back_to_home(self):
        """两条二级页链路各自返回后都应落回首页壳。"""
        self.userA.ensure_logged_in_on_home()
        # 链路①：首页搜索入口 → 搜索页 → 返回 → 首页
        self.userA.click_image(SWAN_HOME_MUSIC_SEARCH_BAR, timeout=10)
        self.userA.image_exists(SWAN_SEARCH_SUBMIT, timeout=10)
        self.userA.press_back()
        self.userA.assert_on_home()
        # 链路②：首页「我喜欢」卡片 → 我喜欢页 → 返回 → 首页
        self.userA.open_home_card("我喜欢")
        self.userA.text_exists("宝藏音乐，随心收藏", timeout=10)
        self.userA.press_back()
        self.userA.assert_on_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
