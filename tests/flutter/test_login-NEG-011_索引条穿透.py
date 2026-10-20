# CASE-ID: login-NEG-011
"""Swan 回归·会话与登录:区号页手势扩展 A 索引条穿透定案(login-NEG-011)。

步骤→AW 映射:
1. 进区号页(open_area_page) → [OCR]「选择归属地」在 + 索引条呈现探针
   (index_bar_letters:OCR 离散单字母 ≥3 个;索引条无注册模板/运行时无
   content-desc,OCR 为唯一合法探针);
2. 索引条单字母穿透点击(OCR 读到的单字母 → click_text 该字母):
   定案=穿透选行生效 → 自动返回登录页(assert:标题消失+「密码登入」[OCR] 在)
   + 区号回填(read_backfill_area_code [OCR] +NNN)。
注:S3 越界拖拽 / S4 空白区点击为 YAML 自标「探针-执行回填」步——元素锚定
   滑动(drag_on_template)仅支持模板矩形内比例滑动,越界/空白区无锚点通道,
   登记 report.notes 不落断言;穿透选中在 POS-022 记为存疑,本条按其自身
   定案口径断言返回,若真机复现存疑态将以明确失败信息暴露。
cleanup: 经回填区号重返区号页选中国行,复位 +86(用例私有清理)。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p02 import SwanRP02Mixin


class TestIndexBarLetterPassThrough(SwanRP02Mixin, BaseTest):

    def setup(self) -> None:
        self.userA = self.users("swanuserA")

    def teardown(self) -> None:
        pass

    def test_index_bar_letter_pass_through(self) -> None:
        # 步骤 1:进区号页 + 索引条呈现探针
        self.userA.ensure_fresh_sms_form()
        self.userA.open_area_page("+86")
        letters = self.userA.index_bar_letters(timeout=10)
        assert len(letters) >= 3, f"索引条单字母 OCR 探针不足(索引条未呈现?): {letters}"
        # 步骤 2:单字母穿透点击 → 定案返回登录页并回填
        target = letters[len(letters) // 2]
        self.userA.click_text(target, timeout=10)
        assert self.userA.find_text_by_ocr("选择归属地", timeout=5) is None, (
            f"穿透字母 {target!r} 后仍停留区号页(与穿透选行定案相悖,存疑面暴露)")
        assert self.userA.find_text_by_ocr("密码登入", timeout=5) is not None, (
            "穿透后未落回登录页")
        code = self.userA.read_backfill_area_code(timeout=10)
        assert code is not None, "穿透选行后区号按钮未回填"
        # 用例私有清理:复位 +86
        self.userA.open_area_page(code)
        self.userA.select_china_area_row()
        assert self.userA.find_text_by_ocr("+86", timeout=5) is not None, (
            "清理复位中国行后区号未恢复 +86")
