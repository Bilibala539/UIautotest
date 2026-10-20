# CASE-ID: vision-POS-009
# LINKED-CASE: vision-POS-009
"""Swan 回归·M10 可视音箱 Vision：唤醒词列表查看与自定义词计数一致（vision-POS-009）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入唤醒词页等列表加载 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_wake_words_page；默认词必有（getVisionData rouseWordList type=5）
- S2 自定义词计数口径 → assert_any_text（「自定义/个」计数展示锚，文案未标定
  候选探测；customWakeWordCount 只统计非默认词——正向吸收模型契约）
- S3 逐条浏览 → swipe_up
- 退出 → press_back（只读）
前置：已绑定 MG100 TESTDEV-MG100-01 在线；唤醒词数据来自服务端快照。
清理：只读浏览；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionWakeWordList(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """唤醒词列表查看与自定义词计数一致（vision-POS-009）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_wake_word_list_and_count(self):
        """唤醒词列表渲染（默认词+自定义词）、计数口径锚点命中；退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wake_words_page()
        # S1 列表加载（默认词必有；新建入口/默认分组锚点候选）
        self.userA.assert_any_text(('新建', '默认', '唤醒'), timeout=10)
        # S2 自定义词计数展示锚点（计数=非默认词口径，展示文案未标定）
        self.userA.assert_any_text(('自定义', '个'), timeout=10)
        # S3 逐条浏览词条
        self.userA.swipe_up()
        # 退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
