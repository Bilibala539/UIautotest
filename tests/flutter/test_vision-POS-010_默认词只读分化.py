# CASE-ID: vision-POS-010
# LINKED-CASE: vision-POS-010
"""Swan 回归·M10 可视音箱 Vision：默认唤醒词只读与自定义词可操作分化展示（vision-POS-010）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1-S2 分化断言 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_wake_words_page 后按数据分支收口：
  - 有「自定义」分区 → 断言「编辑/删除」入口存在（自定义词可操作）
  - 无自定义词（默认词必有）→ 断言全局无「编辑/删除」（默认词只读成立）
  （deleteAiRouseWord 物理删除——禁区 3，全程零触碰）
- S3 零操作退出 → press_back
前置：已绑定 MG100 TESTDEV-MG100-01 在线；默认词必有，自定义词可无（数据分支）。
清理：零删除零编辑退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionDefaultWordReadonly(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """默认唤醒词只读与自定义词可操作分化展示（vision-POS-010）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_default_word_readonly_differentiation(self):
        """自定义分区存在则编辑/删除入口存在；无自定义词则全局只读；零触碰退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_wake_words_page()
        # 数据分支：自定义分区是否可见（自定义词可无——无则统计口径为 0）
        has_custom = self.userA.find_text_by_ocr('自定义', timeout=3) is not None
        if has_custom:
            # S2 自定义词具备编辑/删除入口（与默认词分化对比）
            self.userA.assert_any_text(('编辑', '删除'), timeout=5)
        else:
            # S1 默认词只读成立：全局无编辑/删除入口
            self.userA.text_not_exists('编辑', timeout=3)
            self.userA.text_not_exists('删除', timeout=3)
        # S3 零操作退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
