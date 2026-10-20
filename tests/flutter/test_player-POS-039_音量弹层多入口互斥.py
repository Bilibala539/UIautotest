# CASE-ID: player-POS-039
"""Swan 回归·播放器：音量弹层多入口互斥——播放页入口开 关 复开（player-POS-039）。

⚠️ 部分转换：步骤1 FM 底部栏入口与步骤3 设备卡片入口为 TBD·语义定位
（未截取元素），未纳入本脚本——缺口登记见 package_report.template_needs；
本脚本覆盖播放页入口弹层「开→关→复开」链路（单飞互斥不误锁的 UI 层
回归面：关闭后可正常复开、无残留锁）。

步骤 → AW 映射：
- 前置 Wi-Fi 音箱输出播放页 → preset_playing("wifi_device") + open_player_page()
- 播放页入口打开弹层（单实例）→ open_volume_popup()（图标模板链点击 +
  弹层锚 [图] 断言）
- 关闭弹层 → press_back() + find_image(SWAN_PLAYER_VOLUME_POPUP) 为 None
  （弹层确已关闭）
- 复开（互斥不误锁——单飞 future 释放）→ open_volume_popup()（复开成功=
  无残留锁，不叠第二实例以弹层锚单命中为 UI 层口径）
- 收尾 关闭还原 → press_back()
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYER_VOLUME_POPUP
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestVolumePopupEntryMutex(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """音量弹层多入口互斥——播放页入口（POS-039）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_volume_popup_entry_mutex(self):
        """播放页入口音量弹层：打开 → 关闭 → 复开（单飞不误锁）。"""
        self.userA.preset_playing("wifi_device")
        self.userA.open_player_page()
        # 播放页入口打开弹层（单实例：弹层锚命中）
        self.userA.open_volume_popup()
        # 关闭弹层（确已关闭）
        self.userA.press_back()
        assert self.userA.find_image(SWAN_PLAYER_VOLUME_POPUP, timeout=3) is None, (
            "音量弹层关闭后锚仍命中（弹层未关/残留？）")
        # 复开：互斥不误锁——单飞 future 释放后可正常复开
        self.userA.open_volume_popup()
        # 收尾：关闭还原
        self.userA.press_back()
        # 清理：停止播放
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已停止播放）。"""
        pass
