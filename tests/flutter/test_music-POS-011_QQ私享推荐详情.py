# CASE-ID: music-POS-011
"""Swan 回归·M07 QQ音乐:QQ 私享推荐详情页主路径(music-POS-011)。

步骤→AW 映射(/music_platform/qq/private-recommend):
  1. QQ 主页点私享推荐入口 → open_platform_home('qq') + scroll_to_text
     ('私人推荐')(KB:横滑大卡区块「每日30首/个性化推荐」) + click_text
     ('私人推荐') → 私享推荐详情页打开
  2. 推荐内容加载渲染 → assert_any_text(['推荐','每日','个性化'])(详情
     页内容变体锚 B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:私享推荐详情页专属锚未截模板(KB 仅验证主页横滑卡存在性,
区块标题点击进详情为未验证路径),变体锚承载;页面专属锚真机补截后收紧
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos011QqPrivateRecommend(BaseTest):
    """QQ 私享推荐详情页主路径可达,推荐内容渲染正常。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_qq_private_recommend_detail(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        if self.userA.platform_row_state("qq") != "authorized":
            pytest.skip("QQ 行非已授权态,QQ 主页私享推荐入口不可达(账号态自适配)")
        # 步骤 1:QQ 主页 → 私人推荐区块 → 私享推荐详情页
        self.userA.open_platform_home("qq")
        self.userA.scroll_to_text("私人推荐")
        self.userA.click_text("私人推荐", timeout=8)
        # 步骤 2:推荐内容加载渲染
        self.userA.assert_any_text(["推荐", "每日", "个性化"])
