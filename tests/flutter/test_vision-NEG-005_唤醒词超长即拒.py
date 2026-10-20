# CASE-ID: vision-NEG-005
# LINKED-CASE: vision-NEG-005
"""Swan 回归·M10 可视音箱 Vision：唤醒词超长——非中文超 30 字符输入层即拒（vision-NEG-005）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_wake_words_page
- S1 新建输入 31 字符非中文串 → open_wake_word_create_form + input_text(31 字符)，
  断言 30 位前缀上屏、31 位整体被拒（maxLength 30 输入层收敛）
- S2 清空后输入 30 字符边界值 → clear_input + input_text(30 字符)，断言完整上屏
- S3 编辑已有自定义词超长 → 依赖环境自定义词条目（数据分支），编辑态边界
  与默认词不可编辑契约由 vision-POS-010 分化展示覆盖，本用例覆盖新建态边界
前置：已绑定 MG100 TESTDEV-MG100-01（需人工预置专用设备）——未绑定态 Vision
域无任何入口（knowledge/swan/pages/swan_Vision域不可达页.md 实测）。
清理：不保存退出（提交与否归 vision-NEG-015 服务端上限域）；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionWakeWordOverlong(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """唤醒词超长——非中文超 30 字符输入层即拒（vision-NEG-005）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_wake_word_overlong_rejected(self):
        """新建唤醒词 31 字符输入层即拒、30 字符边界可输入；不保存退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wake_words_page()
        self.userA.open_wake_word_create_form()
        # S1 输入 31 字符非中文串：输入层即拒第 31 位，仅 30 位上屏
        self.userA.input_text('abcdefghijabcdefghijabcdefghijZ')
        self.userA.text_exists('abcdefghijabcdefghijabcdefghij', timeout=5)
        self.userA.text_not_exists('abcdefghijabcdefghijabcdefghijZ', timeout=3)
        # S2 清空后输入 30 字符边界值：完整输入
        self.userA.clear_input()
        self.userA.input_text('abcdefghijabcdefghijabcdefghij')
        self.userA.text_exists('abcdefghijabcdefghijabcdefghij', timeout=5)
        # 不点保存直接返回（零写——aiRouseWord 零触发）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
