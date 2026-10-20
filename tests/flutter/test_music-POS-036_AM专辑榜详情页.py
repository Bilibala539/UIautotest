# CASE-ID: music-POS-036
"""Swan 回归·M07 Apple Music:专辑榜详情页(专辑榜分型)(music-POS-036)。

步骤→AW 映射(/music_platform/apple_music/album_chart_detail,AppleMusicDetailRoutePage 分型):
  1. AM 主页点入口 → open_platform_home('apple')(AM 平台可用态未满足时
     helper 自适配跳过=SKIP-AUTH 闸门) + 入口变体探测 ["专辑榜", "专辑"]
     取首个命中项点击 → 详情页打开
  2. 内容加载渲染 → assert_any_text(["专辑", "榜单"])(落页变体锚 B 口径,
     不触发视频/音频实播,归 M18 交界不越界)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:AM 主页无知识库页面档案(全站未探索),入口/落页锚为变体
B 口径;页面专属锚真机补截后收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

from conftest import BaseTest


class TestMusicPos036AmDetailPage(BaseTest):
    """AM 专辑榜详情页 主路径可达,内容渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_am_detail_page_reachable(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:AM 主页 → 入口变体探测点击
        self.userA.open_platform_home("apple")
        entry = None
        for word in ["专辑榜", "专辑"]:
            entry = self.userA.find_text_by_ocr(word, timeout=2)
            if entry is not None:
                break
        assert entry is not None, (
            "AM 主页未扫到入口(变体词均未命中;主页区块 [图] 模板待补截,"
            "见 package_report.json template_needs)")
        self.userA.tap(entry[0], entry[1])
        # 步骤 2:详情内容渲染(落页变体锚)
        self.userA.assert_any_text(["专辑", "榜单"])
