# CASE-ID: vision-POS-003
# LINKED-CASE: vision-POS-003
"""Swan 回归·M10 可视音箱 Vision：唤醒词页可达与列表渲染（vision-POS-003）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入唤醒词页 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_wake_words_page（入口 OCR「唤醒词」→ 落地锚）
- S2 列表渲染 → assert_any_text（「新建」入口/「默认」分组锚，文案未标定候选探测）
- S3 退出 → press_back
前置：已绑定 MG100 TESTDEV-MG100-01 在线（Vision 入口依赖）。
清理：只读浏览；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionWakeWordsPage(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """唤醒词页可达与列表渲染（vision-POS-003）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_wake_words_page_reachable(self):
        """唤醒词页落地、列表渲染（默认词必有）；退出顺畅。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wake_words_page()
        # S1+S2 页面落地且列表渲染（新建入口/默认词分组锚点候选探测）
        self.userA.assert_any_text(('新建', '默认', '唤醒'), timeout=10)
        # S3 退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
