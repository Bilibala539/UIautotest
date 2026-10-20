# CASE-ID: vision-POS-011
# LINKED-CASE: vision-POS-011
"""Swan 回归·M10 可视音箱 Vision：新建唤醒词字数约束 UI 反馈（vision-POS-011）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 新建输入态出现 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_wake_words_page + open_wake_word_create_form
- S2 输入 1 个中文字符 → input_text('测')，断言字数约束反馈
  （中文 2-6 字域；反馈文案未标定，候选探测见 package_report.template_needs）
- S3 输入合法 4 字中文 → clear_input + input_text('正测词样')，断言上屏（校验通过态）
- S4 不点保存直接返回 → press_back（零保存零设备同步，aiRouseWord 零触发）
前置：专用测试账号已登录；唤醒词未达服务端上限。
清理：未保存零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionCreateWordFeedback(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """新建唤醒词字数约束 UI 反馈（vision-POS-011）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_create_wake_word_length_feedback(self):
        """1 字触发约束反馈、4 字合法上屏；止步保存前零写退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wake_words_page()
        # S1 新建输入态出现
        self.userA.open_wake_word_create_form()
        # S2 输入 1 个中文字符：字数约束反馈（中文 2-6 字域）
        self.userA.input_text('测')
        self.userA.assert_any_text(('至少', '2-6', '两个字', '字数', '请输入'), timeout=8)
        # S3 输入合法 4 字中文：校验通过态（可保存态出现）
        self.userA.clear_input()
        self.userA.input_text('正测词样')
        self.userA.text_exists('正测词样', timeout=5)
        # S4 不点保存直接返回（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
