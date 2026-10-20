# CASE-ID: music-POS-016
"""Swan 回归·M07 QQ音乐:QQ 标签歌单页主路径·参数透传契约(music-POS-016)。

步骤→AW 映射(/music_platform/qq/playlist-by-label,QqPlaylistByLabelArgs
title+labelId 参数契约):
  1. 歌单分类页点一个标签 → open_platform_home('qq') + click_text('歌单')
     → OCR 扫宫格取首个非「全部」标签文本项(运行时数据,服务端 tag 集合
     自适应)并点击 → 标签歌单页打开
  2. 标题栏=入参 title → find_text_by_ocr(所点标签文本)(参数透传:点击的
     标签名即标题,运行时变量锚)
  3. 列表按 labelId 渲染 → _wait_list_settled 等价稳态+变体文案锚

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:分类宫格标签项为 OCR 文本项自适应(服务端 tag 集合未知),取
首个 2-6 字非导航文本;宫格 [图] 模板与页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos016QqPlaylistByLabel(BaseTest):
    """QQ 标签歌单页按 title+labelId 参数契约渲染,透传生效。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_playlist_by_label_passthrough(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页歌单入口不可达(账号态自适配)")
        # 步骤 1:歌单分类页 → 首个可选标签(运行时数据自适应)
        self.userA.open_platform_home("qq")
        self.userA.click_text("歌单", timeout=8)
        assert self.userA.find_text_by_ocr("全部", timeout=10) is not None, (
            "歌单分类页未出现(宫格未渲染,标签选择无承载)")
        items = self.userA.ocr_scan_page()
        tag = None
        for it in items:
            text = it["text"].strip()
            if text in ("全部", "歌单", "分类", "搜索") or "歌单" in text:
                continue
            if text.isdigit() or len(text) < 2 or len(text) > 6:
                continue
            tag = it
            break
        assert tag is not None, (
            "歌单分类页未扫到可选标签文本项(服务端 tag 集合空或 OCR 缺失;"
            "宫格 [图] 模板待补截,见 package_report.json template_needs)")
        self.userA.tap(tag["cx"], tag["cy"])
        # 步骤 2:标题栏=入参 title(点击的标签文本,运行时变量锚)
        assert self.userA.find_text_by_ocr(tag["text"].strip(), timeout=10) \
            is not None, (
            f"标签歌单页标题未渲染入参 title「{tag['text'].strip()}」"
            "(参数透传失效或页面未打开)")
        # 步骤 3:列表按 labelId 数据源渲染(稳态+变体锚)
        self.userA.assert_any_text(["歌单", "播放"])
