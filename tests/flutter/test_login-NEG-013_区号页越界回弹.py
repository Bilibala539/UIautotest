# CASE-ID: login-NEG-013
"""Swan 回归·会话与登录:区号页手势扩展 B——越界回弹与行选择回填(login-NEG-013)。

步骤→AW 映射(ADD1 复审捞回;YAML 原判「手势扩展 B:越界回弹探针」):
1. 短信形态点区号按钮「+86」进入区号选择页(open_area_page,标题锚
   「选择归属地」[OCR]);
2. swipe_up(500) 有界循环滚到底(≤60 次,连续两次整屏 OCR 无变化判稳
   即到底;60 次上限=24000px 远超全列表高度,兜底必达) → 越界探针:
   到底后继续 swipe_up ×3,断言「选择归属地」仍在屏(越界不崩溃不
   白屏,回弹面);
3. swipe_down(500) 有界循环滚回顶(同判稳) → 越界探针:继续 swipe_down
   ×3,断言「选择归属地」仍在(顶部越界回弹面);
4. 行选择回填:OCR 收集当前屏「+NNN」区号行,取首个非「+86」的行码
   click_text 点选(select_area_row,断言自动返回登录页) →
   read_backfill_area_code 断言回填值=所选行码且 ≠「+86」。
注:区号列表数据源为 MXNZP 接口,接口失败时回退内置 4 行静态态——
   本条全流程仅依赖「有行可选 + 手势滚动」,两态天然兼容,无需区分;
   swipe_up/swipe_down 为 AWBase 基础手势(距离参数),非坐标点击。
cleanup: open_area_page(回填号) → select_china_area_row 还原「+86」;
   未登录态保持,无遗留态。
"""
from __future__ import annotations

import re

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p02 import SwanRP02Mixin

_AREA_ROW_RE = re.compile(r"\+\d{2,3}")


class TestAreaPageBounceAndSelect(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def _screen_signature(self) -> str:
        """整屏 OCR 文本签名(滚动判稳用)。"""
        return "|".join(sorted(
            str(item.get("text", "")) for item in self.userA.ocr_scan_page()))

    def _swipe_until_stable(self, direction: str, max_rounds: int = 60) -> None:
        """同向 swipe 有界滚动直至整屏 OCR 连续两轮无变化(到底/回顶)。"""
        prev = None
        stable = 0
        for _ in range(max_rounds):
            if direction == "up":
                self.userA.swipe_up_step(500)
            else:
                self.userA.swipe_down_step(500)
            sig = self._screen_signature()
            if sig == prev:
                stable += 1
                if stable >= 2:
                    return
            else:
                stable = 0
            prev = sig
        assert False, (
            f"区号页 swipe_{direction} {max_rounds} 轮内未判稳(列表未到底/回顶?)")

    def _overshoot_probe(self, direction: str, rounds: int = 3) -> None:
        """越界探针:边缘继续同向滑动后页面仍存活(标题锚在屏)。"""
        for _ in range(rounds):
            if direction == "up":
                self.userA.swipe_up_step(500)
            else:
                self.userA.swipe_down_step(500)
        assert self.userA.find_text_by_ocr("选择归属地", timeout=10) is not None, (
            f"边界越界 swipe_{direction} ×{rounds} 后区号页异常(标题锚消失, "
            "越界回弹面相悖)")

    def _pick_non_default_row_code(self) -> str:
        """OCR 收集当前屏区号行,取首个非「+86」行码;不足则上滑一屏重扫。"""
        for attempt in range(2):
            codes: list[str] = []
            for item in self.userA.ocr_scan_page():
                m = _AREA_ROW_RE.search(str(item.get("text", "")))
                if m and m.group(0) != "+86":
                    codes.append(m.group(0))
            if codes:
                return codes[0]
            self.userA.swipe_up_step(500)
        assert False, "区号页两屏内未找到非「+86」区号行(列表数据异常?)"

    def test_area_page_bounce_and_select(self) -> None:
        # 步骤 1:进入区号选择页
        self.userA.ensure_fresh_sms_form()
        self.userA.open_area_page("+86")
        # 步骤 2:滚到底 + 底部越界探针
        self._swipe_until_stable("up")
        self._overshoot_probe("up")
        # 步骤 3:滚回顶 + 顶部越界探针
        self._swipe_until_stable("down")
        self._overshoot_probe("down")
        # 步骤 4:点选非默认区号行,断言回填切换
        picked = self._pick_non_default_row_code()
        self.userA.select_area_row(picked)
        backfill = self.userA.read_backfill_area_code(timeout=10)
        assert backfill == picked, (
            f"区号回填不符:点选 {picked} 后读到 {backfill}(回填链路相悖)")
        # cleanup:经页内还原「+86」
        self.userA.open_area_page(picked)
        self.userA.select_china_area_row()
        restored = self.userA.read_backfill_area_code(timeout=10)
        assert restored == "+86", f"清理还原失败:区号仍为 {restored}"
