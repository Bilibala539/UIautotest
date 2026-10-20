# CASE-ID: radio-POS-015
"""Swan 回归·电台：全国电台播放发起统一播放链（radio-POS-015）。

步骤 -> AW 映射（countryStationToSong 包装 dataType=fm/terraceType=0
进 /player/unifiedMusic；禁区 1/3：FM 直播流 ≤30s 短会话显式停止，
播放历史上传留服务端痕迹无清理通道——用例只读收尾停止）：
- 步骤1 全国台列表点击任一电台卡片 -> tap_first_list_item
  （TEST-SYNTHETIC 语义：取列表首个可用电台，运行时 OCR 选择）；
- 步骤2 断言起播 UI 态 -> assert_playing（播放态双证据由业务层
  承担）+ assert_any_of_texts 所点电台名（曲名=电台名映射展示面）；
- 步骤3 短会话显式停止 -> player_control('pause')（暂停即断流收尾，
  不可 seek 无进度语义，不做进度断言）。

清理：显式停止播放（步骤3 内完成）；teardown 按 pass（冷启动由
框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioNationalPlay(BaseTest):
    """radio-POS-015：全国台起播、曲名归因、短会话停止。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_national_station_play(self):
        """点电台卡片起播，播放页曲名=电台名，显式停止收尾。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 步骤1：点击首个可用电台卡片（统一播放链包装）
        station = self.userA.tap_first_list_item("城市", "全部")
        # 步骤2：起播 UI 态（playing + 曲名=电台名）
        self.userA.assert_playing()
        self.userA.assert_any_of_texts(station, timeout=10)
        # 步骤3：FM 短会话显式停止（暂停断流收尾）
        self.userA.player_control("pause")
        self.userA.assert_paused()

    def teardown(self) -> None:
        """播放已显式停止（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
