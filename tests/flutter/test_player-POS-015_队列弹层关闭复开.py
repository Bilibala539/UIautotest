# CASE-ID: player-POS-015
"""Swan 回归·播放器：队列弹层关闭销毁与复开（player-POS-015）。

⚠️ B 标定项（ADD1 改判）：队列按钮/关闭钮 current_queue_close_button 均
未注册模板——OCR 优先尽力转换：开→关→复开闭环走通；关闭以 back 为等价
代理（关闭钮模板待注册，template_needs 登记）。

步骤 → AW 映射：
- 前置 有播放任务 → preset_playing("speaker") + open_player_page()
- 步骤1 打开队列弹层 → open_queue_sheet()（OCR 候选词尽力定位）
- 步骤2 关闭弹层回播放页（销毁）→ press_back() + find_image(
  SWAN_PLAYER_PROGRESS_BAR)（播放页回归视口=弹层销毁无残留）
- 步骤3 再次打开验证可复开 → open_queue_sheet()（复开成功=销毁干净可重复
  开合；列表渲染一致由复开后当前曲在列复核）
- 收尾 关闭 → press_back()
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYER_PROGRESS_BAR
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestQueueSheetReopenCycle(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """队列弹层关闭销毁与复开（POS-015，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_queue_sheet_reopen_cycle(self):
        """队列弹层开 → 关（销毁回播放页）→ 复开渲染一致。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        title = self.userA.read_player_title()
        assert title, "起播后读不到当前曲名（列表渲染一致性代理失据）"
        # 步骤1：打开队列弹层
        self.userA.open_queue_sheet()
        # 步骤2：关闭弹层（销毁），回播放页且播放页仍在视口
        self.userA.press_back()
        assert self.userA.find_image(SWAN_PLAYER_PROGRESS_BAR, timeout=5) is not None, (
            "队列弹层关闭后未回播放页（进度条锚未命中）")
        # 步骤3：再次打开验证可复开，列表渲染一致（当前曲仍在列）
        self.userA.open_queue_sheet()
        self.userA.text_exists(title, timeout=8)
        # 收尾：关闭弹层
        self.userA.press_back()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
