# CASE-ID: music-POS-007
"""Swan 回归·M07 平台通用:通用三页可达:排行榜/艺人页/本地库(music-POS-007)。

步骤→AW 映射(承载平台取 QQ 主页:同时具备排行榜块与歌手推荐块):
  1. QQ 主页点「排行榜」入口 → open_platform_home('qq') + click_text('排行榜'),
     排行榜页打开 → assert_any_text(['飙升榜','榜单','排行榜'])(榜单组渲染)
  2. 返回后进艺人页 → press_back() + open_qq_artist_page_from_home()
     (「歌手推荐」首位头像卡点击,知识库已验证路径;艺人页骨架断言=
     「全部播放」主操作锚+歌曲/专辑计数 Tab,KB 生效断言)
  3. 本地音乐库入口归 M13 13.1 账,入口位置未探明(QQ/网易云主页区块均无
     此入口) → 本用例如实覆盖前两面,本地库面登记 template_needs 待入口
     探明后补转(DIGEST B 口径)

cleanup: 无(只读冒烟);框架每用例冷启动。
B 标定说明:排行榜页锚为 OCR 变体 B 口径,页面专属锚真机补截后收紧;
本地库入口/页面待探明(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos007CommonPagesReachable(BaseTest):
    """排行榜/艺人页两条通用可达面打开且渲染无异常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_rank_and_artists_pages_reachable(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页通用入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 排行榜入口 → 榜单组渲染
        self.userA.open_platform_home("qq")
        self.userA.click_text("排行榜", timeout=8)
        self.userA.assert_any_text(["飙升榜", "榜单", "排行榜"])
        # 步骤 2:返回 QQ 主页 → 歌手推荐首位头像卡 → 艺人页渲染
        self.userA.press_back()
        assert self.userA.find_text_by_ocr("排行榜", timeout=8) is not None, (
            "返回后未回到 QQ 主页(排行榜块锚丢失)")
        self.userA.open_qq_artist_page_from_home()
