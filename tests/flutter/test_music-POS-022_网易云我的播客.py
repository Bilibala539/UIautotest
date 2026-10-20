# CASE-ID: music-POS-022
"""Swan 回归·M07 网易云:我的播客页主路径(music-POS-022,需已授权账号)。

步骤→AW 映射(/music_platform/netease/my-podcast):
  1. 网易云主页点我的播客入口 → open_platform_home('netease')(网易云已
     授权为环境常态,未授权由 helper 自适配跳过=SKIP-AUTH 闸门) +
     click_text('我的播客')(KB:用户收藏区四卡之一 我喜欢/自建歌单/
     收藏歌单/我的播客) → 我的播客页打开
  2. 用户播客数据加载(空态为合法态) → 页面锚存在性+稳态承载,空态不断言
     数据非空
  3. 无授权弹层误弹 → assert_no_auth_error()

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:用户收藏区卡片点击进页为未验证路径(KB 仅验证存在性),
我的播客页专属锚未截模板,以「播客」变体锚承载
(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos022NeteaseMyPodcast(BaseTest):
    """网易云我的播客页(已授权账号)主路径可用,无授权弹层误弹。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_my_podcast(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:网易云主页 → 用户收藏区「我的播客」卡
        self.userA.open_platform_home("netease")
        self.userA.scroll_to_text("用户收藏")
        self.userA.click_text("我的播客", timeout=8)
        # 步骤 2:页面挂载(空态为合法态,不断言数据非空)
        assert self.userA.find_text_by_ocr("播客", timeout=10) is not None, (
            "点击「我的播客」后页面未挂载(「播客」锚未命中)")
        self.userA.assert_no_auth_error()
