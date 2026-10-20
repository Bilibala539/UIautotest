# CASE-ID: radio-POS-016
"""Swan 回归·电台：80er/90s 电台播放发起双通道（radio-POS-016）。

步骤 -> AW 映射（harmonyStationToSong：80er fmTypeCode/terraceType=6，
90s terraceType=5，切源 stop→playing→stopped 三连不冒充新源）：
- 步骤1 80er 页点击任一电台卡片 -> tap_card_by_texts 进 80er 页 +
  tap_first_list_item（首个可用电台）+ assert_playing；
- 步骤2 返回后 90s 页点击任一电台卡片 -> press_back x2 回电台 Tab +
  tap_card_by_texts 进 90s 页 + tap_first_list_item + assert_playing
  （播放页曲名=电台名以 assert_any_of_texts 归因）；
- 步骤3 短会话显式停止 -> player_control('pause')（禁区 1：FM ≤30s
  计时收尾；切台断源由统一播放链契约承担）。

清理：显式停止播放（步骤3 内完成）；teardown 按 pass。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioHarmonyDualPlay(BaseTest):
    """radio-POS-016：80er/90s 双通道起播与短会话收尾。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_harmony_dual_channel_play(self):
        """80er/90s 各起播一台，停止收尾。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1：80er 通道起播
        self.userA.tap_card_by_texts("80后", "80后电台", "80er", "80")
        self.userA.tap_first_list_item("全部")
        self.userA.assert_playing()
        # 步骤2：返回后 90s 通道起播（切台断源）
        self.userA.press_back()
        self.userA.press_back()
        self.userA.tap_card_by_texts("90后", "90后电台", "90er", "90")
        station90 = self.userA.tap_first_list_item("全部")
        self.userA.assert_playing()
        self.userA.assert_any_of_texts(station90, timeout=10)
        # 步骤3：FM 短会话显式停止
        self.userA.player_control("pause")
        self.userA.assert_paused()

    def teardown(self) -> None:
        """播放已显式停止（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
