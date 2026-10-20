# CASE-ID: music-POS-027
"""Swan 回归·M07 Qobuz:内容列表页主路径·source 契约+筛入口恒在(music-POS-027)。

步骤→AW 映射(/music_platform/qobuz/content-list,QobuzContentListArgs
source+genreIds 契约,supportsGenreFilter 恒 true):
  1. Qobuz 主页点任一内容区块进列表 → open_platform_home('qobuz') +
     OCR 探测主页内容区块词(推荐/精选/新歌/热门/榜单/歌单 变体,取首个
     命中项点击,运行时数据自适应) → 内容列表页打开
  2. 列表按 source 渲染 → 页面锚+稳态承载(来源参数为路由内参,无 UI
     直观文案,B 口径以列表区变体锚承载)
  3. 曲风筛入口恒在 → assert_any_text(['筛选','曲风','风格'])
     (supportsGenreFilter 恒 true 的 UI 面)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:Qobuz 主页与内容列表页无知识库页面档案(全站未探索),区块
词/落页锚/筛入口锚全为变体 B 口径;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos027QobuzContentList(BaseTest):
    """Qobuz 内容列表页按 source 契约渲染,曲风筛入口恒可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_content_list(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:Qobuz 主页 → 任一内容区块(OCR 变体词探测,运行时自适应)
        self.userA.open_platform_home("qobuz")
        block = None
        for word in ("推荐", "精选", "新歌", "热门", "榜单", "歌单"):
            block = self.userA.find_text_by_ocr(word, timeout=1)
            if block is not None:
                break
        assert block is not None, (
            "Qobuz 主页未扫到任一内容区块词(推荐/精选/新歌/热门/榜单/歌单;"
            "主页区块 [图] 模板待补截,见 package_report.json template_needs)")
        self.userA.tap(block["cx"], block["cy"])
        # 步骤 2:列表按 source 渲染(列表区变体锚)
        self.userA.assert_any_text(["歌单", "榜单", "推荐"])
        # 步骤 3:曲风筛入口恒在(supportsGenreFilter 恒 true)
        self.userA.assert_any_text(["筛选", "曲风", "风格"])
