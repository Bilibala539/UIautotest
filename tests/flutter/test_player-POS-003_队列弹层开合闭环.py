# CASE-ID: player-POS-003
"""Swan 回归·播放器：队列与歌词弹层开合闭环（player-POS-003）。

⚠️ B 标定项（ADD1 改判）：队列按钮为无文案图标且未注册模板、队列弹层与
歌词视图均未探索（知识库「待截/草稿/待复验」）——按 OCR 优先尽力转换，
队列部分走通，歌词视图（步骤4，TBD·语义）留 template_needs 待标定。

步骤 → AW 映射：
- 前置 有播放任务（队列按钮无任务时点击无反应，知识库实测）→ preset_playing("speaker")
  + open_player_page() + read_player_title()（记录当前曲，作队列行渲染代理）
- 步骤1 点击队列按钮 → open_queue_sheet()（OCR 候选词尽力定位；模板待注册）
- 步骤2 队列主体渲染（列表/空态二态）→ text_exists(当前曲名)（有曲目列表
  含当前曲=列表态渲染代理）
- 步骤3 关闭弹层回播放页 → press_back() + find_image(SWAN_PLAYER_PROGRESS_BAR)
  （回全屏播放页无残留；current_queue_close_button 模板待注册，back 为
  等价关闭代理）
- 步骤4 歌词视图（TBD·语义）→ 未纳入，template_needs 登记
清理：显式停止播放（计时收尾）→ player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLAYER_PROGRESS_BAR
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestQueueLyricSheetsOpenClose(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """队列与歌词弹层开合闭环（POS-003，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_queue_lyric_sheets_open_close(self):
        """队列弹层打开 → 当前曲在列 → 关闭回播放页。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        title = self.userA.read_player_title()
        assert title, "起播后读不到当前曲名（队列行渲染代理失据）"
        # 步骤1：打开队列弹层（OCR 候选词尽力定位，模板待注册）
        self.userA.open_queue_sheet()
        # 步骤2：队列主体渲染——当前曲在列表（列表态代理）
        self.userA.text_exists(title, timeout=8)
        # 步骤3：关闭弹层，回全屏播放页（进度条锚确认无残留）
        self.userA.press_back()
        assert self.userA.find_image(SWAN_PLAYER_PROGRESS_BAR, timeout=5) is not None, (
            "队列弹层关闭后未回播放页（进度条锚未命中）")
        # 清理：显式停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
