# CASE-ID: radio-POS-017
"""Swan 回归·电台：播放页合成封面与无歌词形态（radio-POS-017，弱形式正向面）。

步骤 -> AW 映射（RadioCoverView 常量基线：320 外框/124 唱片/46 中心
装饰；unified_player_widget 电台无歌词 playerPageIndex 回 0）：
- 步骤0 前置起播任一全国台电台（承接 015 播放链：tap_first_list_item
  + assert_playing）；
- 步骤1 封面区渲染 -> 合成封面为图像级断言且模板未入库（登记
  package_report.template_needs），OCR 侧以播放页锚点与播放态兜底，
  视觉精比对留图像兜底轮；
- 步骤2 无歌词形态 -> text_not_exists('歌词')（电台无歌词页，
  歌词文案不驻留播放页）；
- 步骤3 封面渲染稳定 -> 无错位崩溃由播放态持续存在兜底（页面存活）；
- 步骤4 短会话显式停止 -> player_control('pause')（禁区 1 收尾）。

清理：显式停止播放；teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioPlayerCoverNoLyric(BaseTest):
    """radio-POS-017：电台播放页无歌词形态与短会话收尾。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_player_no_lyrics_form(self):
        """起播全国台 -> 播放页无歌词文案 -> 显式停止。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 前置：起播首个可用电台（统一播放链）
        self.userA.tap_first_list_item("城市", "全部")
        self.userA.assert_playing()
        # 步骤2：无歌词形态（歌词页不驻留）
        self.userA.text_not_exists("歌词", timeout=3)
        # 步骤3：播放页存活（封面渲染稳定、无错位崩溃兜底）
        self.userA.assert_playing()
        # 步骤4：FM 短会话显式停止
        self.userA.player_control("pause")
        self.userA.assert_paused()

    def teardown(self) -> None:
        """播放已显式停止（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
