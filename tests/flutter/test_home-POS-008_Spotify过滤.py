# CASE-ID: home-POS-008
"""Swan 回归·首页：Spotify 平台不展示于首页(home-POS-008,部分转换)。

步骤→AW 映射：
- 音乐 Tab 全量断言 → go_top_tab('音乐') + text_not_exists('Spotify')
  + swipe_up 翻屏后再断言（有限屏采样遍历）
- 推荐 Tab 全量断言 → go_top_tab('推荐') + text_not_exists('Spotify')
  + swipe_up 翻屏后再断言

⚠️ 部分转换注记：①"遍历所有 Tab"落为推荐/音乐两 Tab 各 2 屏采样（无限
滚动不可穷尽）；②YAML 前置"服务端过滤配置已生效"为服务端造数，依赖现网
数据即满足，用例内不注入。
cleanup：无用例私有清理（冷启动模型）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestSpotifyFilteredOut(SwanRP03Mixin, BaseTest):
    """推荐/音乐 Tab 均 OCR 不到 Spotify（平台过滤生效）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_spotify_not_displayed_on_home(self):
        """音乐 Tab、推荐 Tab 各翻 2 屏，断言均无 Spotify 文案。"""
        self.userA.ensure_logged_in_on_home()

        self.userA.go_top_tab('音乐')
        self.userA.text_not_exists('Spotify', timeout=8)
        self.userA.swipe_up()
        self.userA.text_not_exists('Spotify', timeout=5)

        self.userA.go_top_tab('推荐')
        self.userA.text_not_exists('Spotify', timeout=8)
        self.userA.swipe_up()
        self.userA.text_not_exists('Spotify', timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在推荐 Tab
