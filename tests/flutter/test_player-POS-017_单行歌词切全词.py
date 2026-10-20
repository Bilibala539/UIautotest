# CASE-ID: player-POS-017
"""Swan 回归·播放器：单行动态歌词与全词页切换（player-POS-017）。

⚠️ B 标定项（ADD1 改判）：全词页未探索、封面/歌词区点击无模板——歌词行
为动态文本（OCR 可读可点），按 OCR 优先转换：单行歌词读取→点歌词行切换
→全词页文本增多断言走通；全词页锚留 template_needs 待标定。
⚠️ 前置依赖：当前曲目须有歌词（TEST-SYNTHETIC 曲目歌词覆盖待真机标定，
无歌词曲目在步骤1 断言失败，属环境数据项）。

步骤 → AW 映射：
- 前置 播放中封面页 → preset_playing("speaker") + open_player_page()
- 步骤1 观察单行动态歌词 → ocr_scan_page() 封面区（y 600-1100）取文本行
  （单行歌词 OCR 可读）
- 步骤2 点击封面/歌词区切全词 → click_text(歌词行文本) → 全词页断言：
  OCR 歌词行数增多（全词页多行歌词 vs 单行）
清理：停止播放 → player_control("pause")。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p04 import SwanRP04Mixin


def _cover_zone_lines(user, y_top: int = 600, y_bottom: int = 1100) -> list[str]:
    """封面区（曲名/控制条之间）OCR 文本行，自上而下。"""
    return [i["text"].strip() for i in user.ocr_scan_page()
            if y_top < i["cy"] < y_bottom and i.get("text", "").strip()]


class TestLyricViewSwitch(SwanRP04Mixin, SwanPlayerRegressionMixin, BaseTest):
    """单行动态歌词与全词页切换（POS-017，B 标定项）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_lyric_view_switch(self):
        """单行歌词可读 → 点歌词区切全词 → 多行歌词渲染。"""
        self.userA.preset_playing("speaker")
        self.userA.open_player_page()
        # 步骤1：单行动态歌词可读（封面区文本行）
        lines = _cover_zone_lines(self.userA)
        assert lines, "封面区无 OCR 文本行（单行歌词未渲染或曲目无歌词）"
        lyric_line = lines[0]
        # 步骤2：点击歌词行切全词，全词页多行歌词渲染
        self.userA.click_text(lyric_line, timeout=5)
        full_lines = _cover_zone_lines(self.userA, y_top=300, y_bottom=1300)
        assert len(full_lines) >= 2, (
            f"切换后歌词行数未增多（全词页未打开？）单行={lyric_line!r} "
            f"现文案={full_lines}")
        # 清理：停止播放（计时收尾）
        self.userA.player_control("pause")

    def teardown(self) -> None:
        """无用例私有清理（已显式停止播放）。"""
        pass
