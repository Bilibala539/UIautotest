# CASE-ID: music-POS-017
"""Swan 回归·M07 网易云:每日推荐页主路径·双 Tab+曲风面板(music-POS-017)。

步骤→AW 映射(/music_platform/netease/daily-recommend,modeFromRouteArguments
双 Tab+风格面板):
  1. 网易云主页点每日推荐入口 → open_platform_home('netease')(网易云已授权
     为环境常态) + click_text('每日推荐')(知识库 draft 区块) → 每日推荐页
  2. 双 Tab 结构渲染 → assert_any_text(['默认推荐','风格推荐'])(draft 实测
     双 Tab 文案;内容分别加载以 Tab 文案存在性承载)
  3. 展开风格推荐曲风面板 → click_text('风格推荐') → 面板渲染曲风选项
     → assert_any_text(['流行','民谣','摇滚','电子','曲风'])(曲风选项
     变体锚 B 口径)

cleanup: 无(只读浏览);框架每用例冷启动。
B 标定说明:每日推荐页专属锚与曲风选项集合未截模板,变体锚承载;真机补截
后收紧(见 package_report.json template_needs)。
"""

from __future__ import annotations

import pytest

from conftest import BaseTest


class TestMusicPos017NeteaseDailyRecommend(BaseTest):
    """网易云每日推荐页双 Tab 与曲风面板结构特性可用。"""

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_netease_daily_recommend_tabs(self) -> None:
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("平台")
        # 步骤 1:网易云主页 → 每日推荐区块(未授权态由 helper 自适配跳过)
        self.userA.open_platform_home("netease")
        self.userA.click_text("每日推荐", timeout=8)
        # 步骤 2:双 Tab 结构渲染
        self.userA.assert_any_text(["默认推荐", "风格推荐"])
        # 步骤 3:展开风格推荐曲风面板
        self.userA.click_text("风格推荐", timeout=8)
        self.userA.assert_any_text(["流行", "民谣", "摇滚", "电子", "曲风"])
