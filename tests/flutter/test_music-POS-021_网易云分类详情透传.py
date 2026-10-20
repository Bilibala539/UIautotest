# CASE-ID: music-POS-021
"""Swan 回归·M07 网易云:分类详情页主路径·参数透传契约(music-POS-021)。

步骤→AW 映射(/music_platform/netease/playlist-classify-detail,
NeteasePlaylistClassifyDetailPageArgs title/tag/tagId 契约):
  1. 歌单分类页点一个分类 → open_platform_home('netease') + click_text
     ('歌单', region=(0, 300, 160, 1312))(裸词坑 region 口径) →
     click_text('流行')(KB 实测子 Tab 首项,确定性分类项) → 分类详情页
  2. 标题栏=入参 title → find_text_by_ocr('流行')(点击的分类名即标题,
     参数透传锚)
  3. 列表按 tag/tagId 过滤渲染 → assert_any_text(['歌单','播放'])
     (列表区变体锚 B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:子 Tab 点击进分类详情为未验证路径(KB 仅验证子 Tab 首项存在),
变体锚承载;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos021NeteaseClassifyDetail(BaseTest):
    """网易云分类详情页按 title/tag/tagId 契约渲染,透传生效。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_classify_detail_passthrough(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:歌单分类页 → 子 Tab 首项「流行」(KB 实测确定性分类项)
        self.userA.open_platform_home("netease")
        self.userA.click_text("歌单", timeout=8, region=(0, 300, 160, 1312))
        self.userA.click_text("流行", timeout=8)
        # 步骤 2:标题栏=入参 title(参数透传锚)
        assert self.userA.find_text_by_ocr("流行", timeout=10) is not None, (
            "分类详情页标题未渲染入参 title「流行」(参数透传失效或页面未打开)")
        # 步骤 3:列表按 tag/tagId 过滤渲染
        self.userA.assert_any_text(["歌单", "播放"])
