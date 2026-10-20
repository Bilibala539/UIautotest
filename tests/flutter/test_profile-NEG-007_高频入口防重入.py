# CASE-ID: profile-NEG-007
"""Swan 回归·M13 个人中心：高频入口防重入不卡死（profile-NEG-007）。

用例 → AW 映射（C 级简化转换）：
- YAML 原“快速连点 5 次”时序不可忠实复现，且单实例断言需导航栈检查（OCR 不可观察）→
  记录为执行注记；自动化面转为三高频入口逐一进入+返回 walk（防卡死/崩溃面）：
  扫一扫 → open_scan_page + back_to_me_page；
  本地音乐 → 条件进入（坑19 漂移）+ assert_page_not_blank + back；
  音质设置 → open_quality_sheet + back 关闭。
- 全程无 ANR/崩溃 → assert_no_anr_dialog
清理（G3/G4）：导航类只读用例无私有清理；冷启动由框架夹具承担。
"""

from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p08 import SwanRP08Mixin


class TestProfileNeg007HighFreqEntryReentry(SwanRP08Mixin, BaseTest):
    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def test_high_freq_entry_reentry(self) -> None:
        self.userA.open_me_page()
        # 入口1：扫一扫
        self.userA.open_scan_page()
        self.userA.back_to_me_page()
        # 入口2：本地音乐（坑19 漂移：行可能未渲染，条件跳过）
        if self.userA.me_row_scroll_until("本地音乐"):
            self.userA.click_text("本地音乐")
            self.userA.assert_page_not_blank()
            self.userA.back_to_me_page()
        # 入口3：音质设置（底部弹层）
        self.userA.open_quality_sheet()
        self.userA.close_quality_sheet_by_back()
        self.userA.assert_no_anr_dialog()

    def teardown(self) -> None:
        pass
