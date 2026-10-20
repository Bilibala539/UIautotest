# CASE-ID: vision-POS-024
# LINKED-CASE: vision-POS-024
"""Swan 回归·M10 可视音箱 Vision：电台/酷狗歌词分类差异——0/5/6 电台·4 非电台（vision-POS-024）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_advanced_settings
- S1 电台类平台（terraceType 0/5/6 任一）编辑器 → open_vision_scheme_editor('电台')，
  断言分类项中无歌词（电台正向——_isVisionRadioTerrace 判定）
- S2 酷狗编辑器 → open_vision_scheme_editor('酷狗')，断言有歌词分类（酷狗非电台）
- S3 不保存直接返回 → press_back（零保存退出）
前置：服务端方案平台含电台类（0/5/6 至少一个）与酷狗（terraceType=4）——
缺型平台则对应分支失败暴露（SKIP-DATA 归执行轮环境判定）。
清理：未保存零写退出；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionRadioLyricsDiff(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """电台/酷狗歌词分类差异——0/5/6 电台·4 非电台（vision-POS-024）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_radio_kugou_lyrics_diff(self):
        """电台类编辑器无歌词分类、酷狗编辑器有歌词分类；不保存退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_advanced_settings()
        # S1 电台类平台编辑器：分类项中无歌词（电台正向）
        self.userA.open_vision_scheme_editor('电台')
        self.userA.text_not_exists('歌词', timeout=8)
        self.userA.press_back()
        self.userA.press_back()
        # S2 酷狗编辑器：分类项中有歌词（酷狗非电台）
        self.userA.open_vision_scheme_editor('酷狗')
        self.userA.text_exists('歌词', timeout=10)
        # S3 不保存直接返回（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
