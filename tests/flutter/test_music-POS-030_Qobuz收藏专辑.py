# CASE-ID: music-POS-030
"""Swan 回归·M07 Qobuz:收藏专辑页主路径(music-POS-030,需已授权账号)。

步骤→AW 映射(/music_platform/qobuz/saved-albums):
  1. Qobuz 主页点收藏专辑入口 → open_platform_home('qobuz') + 入口变体
     探测('收藏专辑'/'专辑')点击 → 收藏专辑页打开
  2. 收藏专辑数据加载(空态为合法态) → 页面锚存在性承载,不断言数据非空

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:Qobuz 主页无知识库档案,入口/落页锚为变体 B 口径;页面专属锚
真机补截后收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos030QobuzSavedAlbums(BaseTest):
    """Qobuz 收藏专辑页(已授权账号)主路径可用,专辑列表渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_saved_albums(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:Qobuz 主页 → 收藏专辑入口(变体探测)
        self.userA.open_platform_home("qobuz")
        entry = None
        for word in ("收藏专辑", "专辑"):
            entry = self.userA.find_text_by_ocr(word, timeout=2)
            if entry is not None:
                break
        assert entry is not None, (
            "Qobuz 主页未扫到收藏专辑入口(收藏专辑/专辑变体均未命中;"
            "主页区块 [图] 模板待补截,见 package_report.json template_needs)")
        self.userA.tap(entry["cx"], entry["cy"])
        # 步骤 2:页面挂载(空态为合法态)
        self.userA.assert_any_text(["专辑", "收藏"])
