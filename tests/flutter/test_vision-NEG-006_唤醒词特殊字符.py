# CASE-ID: vision-NEG-006
# LINKED-CASE: vision-NEG-006
"""Swan 回归·M10 可视音箱 Vision：唤醒词特殊字符——正则与中文 2-6 字规则（vision-NEG-006）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_wake_words_page
- S1 输入 emoji → input_text，断言拦截反馈出现或 emoji 未上屏（输入层即拒两形态）
- S2 输入纯符号/空格串 → input_text，同口径断言拦截
- S3 中文边界 2 字/6 字合法对照 → input_text 断言上屏；止步保存前
  （合法对照保存=受控写 aiRouseWord+设备同步——禁区 2，本用例不点保存）
前置：已绑定 MG100 TESTDEV-MG100-01（需人工预置专用设备）。
清理：不保存退出零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin

_HINTS = ('不支持', '无效', '仅支持', '2-6', '中文')


class TestVisionWakeWordSpecialChars(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """唤醒词特殊字符——正则与中文 2-6 字规则（vision-NEG-006）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def _assert_rejected(self):
        """拦截形态二选一：输入层反馈文案出现，或非法字符未上屏。"""
        hint = None
        for h in _HINTS:
            if self.userA.find_text_by_ocr(h, timeout=2) is not None:
                hint = h
                break
        if hint is None:
            self.userA.text_not_exists('😀', timeout=3)

    def test_wake_word_special_chars_rejected(self):
        """emoji/纯符号被拦截；中文 2 字与 6 字边界合法上屏；不保存退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wake_words_page()
        self.userA.open_wake_word_create_form()
        # S1 输入 emoji：中文 2-6 字规则拒绝（反馈文案或未上屏二选一）
        self.userA.input_text('😀🤖')
        self._assert_rejected()
        # S2 输入纯符号/空格串：正则限定拦截
        self.userA.clear_input()
        self.userA.input_text('!@# ')
        self._assert_rejected()
        # S3 中文边界对照：2 字与 6 字均可上屏（可保存态；止步保存前零写）
        self.userA.clear_input()
        self.userA.input_text('知语')
        self.userA.text_exists('知语', timeout=5)
        self.userA.clear_input()
        self.userA.input_text('知语妙音悦耳')
        self.userA.text_exists('知语妙音悦耳', timeout=5)
        # 不点保存直接返回（受控写不触发——禁区 2）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
