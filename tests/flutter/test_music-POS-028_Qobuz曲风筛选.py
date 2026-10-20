# CASE-ID: music-POS-028
"""Swan 回归·M07 Qobuz:曲风筛选页·选中/记住/全选语义(music-POS-028)。

步骤→AW 映射(/music_platform/qobuz/genre-filter,rememberSelection/
allGenresSelected 契约;allGenresSelected 纯 UI 字段不入请求参数不可 UI 验):
  1. 内容列表页打开曲风筛选页 → open_platform_home('qobuz') + 主页区块词
     探测进内容列表(POS-027 同构) + click_text 筛入口变体('筛选'/'曲风')
     → 曲风筛选页打开(锚 ['曲风','全选'])
  2. 勾选一个曲风并确认 → OCR 取首个 2-4 字非导航曲风项点击(运行时数据
     自适应) → click_text 确认钮变体('确认'/'确定'/'完成') → 回列表
  3. 再次进入筛选页(rememberSelection) → 上次勾选保留:勾选态为视觉态
     (勾选框),OCR 不可稳读 → 本步覆盖「再进入可达」,勾选记忆断言登记
     template_needs 待勾选态 [图] 模板后补强(DIGEST B 口径)

cleanup: 清除曲风筛选(恢复全量)——清除入口未标定,由框架冷启动复位。
B 标定说明:Qobuz 筛选页无知识库档案,入口/曲风项/确认钮/勾选态锚全为
变体 B 口径(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos028QobuzGenreFilter(BaseTest):
    """Qobuz 曲风筛选页可达,曲风勾选与确认链路可走通。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qobuz_genre_filter(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:Qobuz 主页 → 内容列表 → 曲风筛选页
        self.userA.open_platform_home("qobuz")
        block = None
        for word in ("推荐", "精选", "新歌", "热门", "榜单", "歌单"):
            block = self.userA.find_text_by_ocr(word, timeout=1)
            if block is not None:
                break
        assert block is not None, (
            "Qobuz 主页未扫到任一内容区块词(主页区块 [图] 模板待补截)")
        self.userA.tap(block["cx"], block["cy"])
        entry = None
        for word in ("筛选", "曲风"):
            entry = self.userA.find_text_by_ocr(word, timeout=2)
            if entry is not None:
                break
        assert entry is not None, (
            "内容列表页未扫到曲风筛入口(筛选/曲风变体均未命中;"
            "筛入口 [图] 模板待补截,见 package_report.json template_needs)")
        self.userA.tap(entry["cx"], entry["cy"])
        self.userA.assert_any_text(["曲风", "全选"])
        # 步骤 2:勾选首个曲风项并确认(运行时数据自适应)
        items = self.userA.ocr_scan_page()
        genre = None
        for it in items:
            text = it["text"].strip()
            if text in ("曲风", "全选", "确认", "确定", "完成", "取消"):
                continue
            if text.isdigit() or len(text) < 2 or len(text) > 4:
                continue
            genre = it
            break
        assert genre is not None, (
            "曲风筛选页未扫到可选曲风文本项(曲风项 [图] 模板待补截,"
            "见 package_report.json template_needs)")
        self.userA.tap(genre["cx"], genre["cy"])
        confirm = None
        for word in ("确认", "确定", "完成"):
            confirm = self.userA.find_text_by_ocr(word, timeout=2)
            if confirm is not None:
                break
        assert confirm is not None, (
            "曲风筛选页未扫到确认钮(确认/确定/完成变体均未命中)")
        self.userA.tap(confirm["cx"], confirm["cy"])
        # 步骤 3:再次进入筛选页(记忆勾选场景:可达性覆盖,勾选态断言待标定)
        entry2 = None
        for word in ("筛选", "曲风"):
            entry2 = self.userA.find_text_by_ocr(word, timeout=3)
            if entry2 is not None:
                break
        assert entry2 is not None, (
            "确认筛选后未回到可再进筛选页的列表(导航栈异常)")
        self.userA.tap(entry2["cx"], entry2["cy"])
        self.userA.assert_any_text(["曲风", "全选"])
