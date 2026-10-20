# CASE-ID: music-POS-018
"""Swan 回归·M07 网易云:歌单分类页主路径·同页分型歌单型(music-POS-018)。

步骤→AW 映射(知识库 10-12 实测口径):
  1. 网易云主页点歌单区块标题 → open_platform_home('netease') +
     click_text('歌单', region=(0, 300, 160, 1312))(⚠️ 裸词坑:全页扫描
     会被用户收藏区「自建歌单」卡抢匹配,KB 实测 region 限定左列口径可用)
     → 歌单分类页打开(顶栏「歌单分类」KB 实测锚)
  2. 分类宫格加载渲染 → assert_any_text(['流行','摇滚'])(KB 实测子 Tab
     首项流行/摇滚行,首项为流行无推荐,与 QQ 分类页差异)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:region 口径为 KB 10-12 实测值,跨分辨率稳健性真机回归时复核;
宫格 [图] 模板待补截(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos018NeteasePlaylistClassify(BaseTest):
    """网易云歌单分类页主路径可达,分类宫格渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_playlist_classify(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:网易云主页 → 歌单区块标题(region 左列限定,裸词坑规避)
        self.userA.open_platform_home("netease")
        self.userA.click_text("歌单", timeout=8, region=(0, 300, 160, 1312))
        # 步骤 2:分类宫格渲染(KB 实测顶栏锚+子 Tab 首项)
        assert self.userA.find_text_by_ocr("歌单分类", timeout=10) is not None, (
            "点击「歌单」后未进入歌单分类页(顶栏「歌单分类」锚未命中;"
            "疑裸词坑误落自建歌单页,region 口径需复核)")
        self.userA.assert_any_text(["流行", "摇滚"])
