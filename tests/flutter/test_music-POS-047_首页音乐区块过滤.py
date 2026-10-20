# CASE-ID: music-POS-047
"""Swan 回归·M07 平台授权:首页音乐区块未授权仍显示(music-POS-047)。

步骤→AW 映射(7.7 目录映射,homeMusicPlatformSpecs 只按 kind!=spotify
过滤+坑 11;全程零点击不进授权链):
  1. 首页音乐 Tab → go_top_tab("音乐")(区块按服务端顺序渲染)
  2. 未授权非 Spotify 平台区块存在性 → assert_any_text(网易云/QQ/酷狗/
     Qobuz/Apple 变体族,≥1 命中;测试账号常态即满足)
  3. Spotify 区块不出现 → text_not_exists("Spotify")(过滤实现 mapper
     生效断言);零点击完成断言,不进授权链

cleanup: 无(只读浏览)。
B 标定说明:首页音乐区块头为服务端目录动态渲染,平台名变体词 B 口径;
区块头专属锚真机补截后收紧,见 package_report.json template_needs。
"""

from __future__ import annotations

from conftest import BaseTest


class TestMusicPos047HomeMusicFilter(BaseTest):
    """首页音乐 Tab 未授权非 Spotify 平台区块不隐藏,Spotify 不出现。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_home_music_block_filter(self) -> None:
        self.userA.ensure_logged_in_on_home()
        # 步骤 1:首页·音乐 Tab(顶 Tab 持久化,显式切换)
        self.userA.go_top_tab("音乐")
        # 步骤 2:未授权非 Spotify 平台区块仍显示(≥1 个)
        self.userA.assert_any_text(
            ["网易云", "QQ", "酷狗", "Qobuz", "Apple"])
        # 步骤 3:Spotify 区块不出现(坑 11 过滤实现,零点击收尾)
        self.userA.text_not_exists("Spotify", timeout=3)
