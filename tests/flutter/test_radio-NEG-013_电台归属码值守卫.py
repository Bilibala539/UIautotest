# CASE-ID: radio-NEG-013
"""Swan 回归·电台：电台归属码值族守卫（radio-NEG-013，UI 可观察面）。

步骤 -> AW 映射（terraceType 0/5/6 码值归属；坑 9：黑盒以来源区块 +
曲名归因断言，展示名不作码值权威——码值语义由 fm_radio_action_adapter
契约承担；禁区 1：FM ≤30s 短会话逐段显式停止；禁区 3：播放历史
uploadType=4 服务端痕迹知晓不清理）：
- 步骤1/2 90s 页点台起播断归属 -> tap_card_by_texts('90后'候选) 进
  90s 页 + tap_first_list_item + assert_playing + assert_any_of_texts
  （播放页曲名=所点电台名，归属不错挂的展示面）；
- 步骤3 80er/全国台同构对照（快切进播放页即停）-> 80er 起播归因 +
  暂停，全国台起播归因 + 暂停（uploadType 固定 '4' 为契约面）；
- 步骤4 停止播放收尾 -> 每段 player_control('pause') 显式断流
  （直播流不 seek 不拖进度）。

清理：播放已在用例内逐段显式停止；teardown 按 pass。
"""
from __future__ import annotations

from conftest import BaseTest


class TestRadioTerraceAttribution(BaseTest):
    """radio-NEG-013：90s/80er/全国台三通道起播归因与逐段停止。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_terrace_attribution(self):
        """三通道逐一起播，曲名归因不错挂，逐段显式停止。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1/2：90s 通道起播归因（terraceType=5 语义）
        self.userA.tap_card_by_texts("90后", "90后电台", "90er", "90")
        station90 = self.userA.tap_first_list_item("全部")
        self.userA.assert_playing()
        self.userA.assert_any_of_texts(station90, timeout=10)
        self.userA.player_control("pause")
        # 步骤3：80er 通道对照（terraceType=6 语义），快切即停
        self.userA.press_back()
        self.userA.press_back()
        self.userA.tap_card_by_texts("80后", "80后电台", "80er", "80")
        station80 = self.userA.tap_first_list_item("全部")
        self.userA.assert_playing()
        self.userA.assert_any_of_texts(station80, timeout=10)
        self.userA.player_control("pause")
        # 步骤3：全国台对照（terraceType=0 语义），快切即停
        self.userA.press_back()
        self.userA.press_back()
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        station00 = self.userA.tap_first_list_item("城市", "全部")
        self.userA.assert_playing()
        self.userA.assert_any_of_texts(station00, timeout=10)
        # 步骤4：停止播放收尾
        self.userA.player_control("pause")
        self.userA.assert_paused()

    def teardown(self) -> None:
        """播放已逐段显式停止（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
