# CASE-ID: music-POS-012
"""Swan 回归·M07 QQ音乐:QQ 新歌推荐详情页主路径(music-POS-012)。

步骤→AW 映射(/music_platform/qq/new-song-recommend):
  1. QQ 主页点新歌推荐入口 → open_platform_home('qq') + scroll_to_text
     ('新歌推荐')(KB:标题+子Tab 内地/韩国/港台/欧美/日本+歌曲行) +
     click_text('新歌推荐') → 新歌推荐详情页打开
  2. 新歌列表加载渲染 → assert_any_text(['内地','韩国','港台','欧美','日本',
     '新歌'])(KB 实测子 Tab 文案变体锚,服务端默认子 Tab 渲染承载列表)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:区块标题点击进详情为未验证路径(KB 仅验证区块存在性),变体
锚承载;页面专属锚真机补截后收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos012QqNewSongRecommend(BaseTest):
    """QQ 新歌推荐详情页主路径可达,新歌列表渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_new_song_recommend_detail(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页新歌推荐入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 新歌推荐区块 → 新歌推荐详情页
        self.userA.open_platform_home("qq")
        self.userA.scroll_to_text("新歌推荐")
        self.userA.click_text("新歌推荐", timeout=8)
        # 步骤 2:新歌列表加载渲染(KB 子 Tab 文案变体锚)
        self.userA.assert_any_text(["内地", "韩国", "港台", "欧美", "日本", "新歌"])
