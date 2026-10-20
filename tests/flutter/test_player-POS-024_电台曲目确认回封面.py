# CASE-ID: player-POS-024
"""Swan 回归·播放器：电台曲目确认后回封面（player-POS-024）。

⚠️ B 标定项（ADD1 改判）：电台 Tab 首页顶部常驻（知识库 首页电台Tab
Wave1 草稿），OCR 文本可走；电台行点击后的播放链路与歌词页锚未探索——
起播断言以播放态收口，歌词切入部分留 template_needs 待标定。
⚠️ 前置依赖：电台内容为在线电台数据（站点可用性属环境项）。

步骤 → AW 映射：
- 步骤1 从电台入口起播一台 FM 电台 → ensure_logged_in_on_home() +
  click_text("电台")（顶部 Tab [OCR]）→ ocr_scan_page() 取含「电台」的
  内容行点击（站电台行，避开顶部 Tab 带）→ 播放页 assert_playing()
- 步骤2 电台播放中切入歌词页 → 未纳入（歌词视图锚未探索，与 POS-017
  同源 template_needs）；以播放连续性复核收口
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


class TestRadioTrackConfirmBackCover(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """电台曲目确认后回封面（POS-024，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_radio_track_confirm_back_cover(self):
        """电台 Tab → 点电台行起播 → 播放态确立（歌词切入留标定）。"""
        self.userA.ensure_logged_in_on_home()
        # 步骤1：进电台 Tab
        self.userA.click_text("电台", timeout=10)
        # 取内容区（顶部 Tab 带之下）首个含「电台」的可点行
        rows = [i for i in self.userA.ocr_scan_page()
                if "电台" in i["text"] and i["cy"] > 400 and i["text"].strip()]
        assert rows, "电台页内容区未探到可点电台行（站点列表未渲染？）"
        self.userA.click_text(rows[0]["text"], timeout=8)
        # 起播断言（电台播放链路真机标定点：行点击即播 or 需再点播放）
        self.userA.assert_playing()
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
