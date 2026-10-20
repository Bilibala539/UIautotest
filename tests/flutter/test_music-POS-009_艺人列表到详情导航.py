# CASE-ID: music-POS-009
"""Swan 回归·M07 平台通用:艺人列表到艺人详情导航(music-POS-009)。

知识库构型说明(swan_艺人页 KB):/music_platform/artists 为单艺人构型
(标题=艺人名,计数 Tab 歌曲/专辑,主操作「全部播放」);"艺人列表"面对应
QQ 主页「歌手推荐」圆头像横滑行(KB 已验证:头像卡 click → 艺人页)。

步骤→AW 映射:
  1. 平台主页艺人列表(歌手推荐头像行)渲染 → open_platform_home('qq')
     + scroll_to_text('歌手推荐'),头像行可见即列表渲染完成
  2. 点击列表首位艺人 → open_qq_artist_page_from_home()(首位头像卡 OCR
     文本项点击,服务端轮换自适应) → 艺人详情挂载(「全部播放」+歌曲/专辑)
  3. 返回艺人列表 → press_back() 后「歌手推荐」区块仍在(状态保持,无重载
     白屏以区块锚承载)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:首位头像卡为 OCR 文本项自适应(服务端轮换),头像卡 [图] 模板
待补截(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos009ArtistListToDetail(BaseTest):
    """艺人列表(歌手推荐行)→首位艺人详情→返回,导航链全通状态保持。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_artist_list_to_detail_navigation(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页艺人入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页艺人列表(歌手推荐头像行)渲染
        self.userA.open_platform_home("qq")
        self.userA.scroll_to_text("歌手推荐")
        # 步骤 2:点击列表首位艺人 → 艺人详情挂载
        self.userA.open_qq_artist_page_from_home()
        # 步骤 3:返回艺人列表,状态保持
        self.userA.press_back()
        self.userA.scroll_to_text("歌手推荐")
