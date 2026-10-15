# CASE-ID: aw-进度条跳转_加号_手机扬声器
# LINKED-CASE: REG-023,REG-024
"""Swan 回归·播放器域：进度条拖动/点击跳转（回归用例 23-24）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域3）：
- 用例23-24 拖动/点击进度条跳转 → seek_to(ratio, action="drag"|"click")

断言口径（方案 §5③ 拍板）：声学断言降级为 UI 态——进度按 OCR 双时间核对
已播 ≈ ratio × 总时长。
矩阵：device_type（speaker=手机扬声器默认输出 / wifi_device=rig 音箱
SWAN_DEVICE_NAME）。进度条一律 drag_on_template 元素锚定，不写坐标。
rig 环境变量与公共前置/清理见 utils/aw/business/swan_regression.py。
清理（G3/G4）：关弹层 → 尽力暂停 → 收播放页 → 输出恢复 → 回首页（mixin teardown）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin


SEEK_RATIO = 0.75  # 进度跳转目标比例


class TestSeekProgress(SwanPlayerRegressionMixin, BaseTest):
    """进度条拖动/点击跳转（回归用例 23-24）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_seek_progress(self):
        """用例23-24：进度条拖动/点击跳转到 75%，OCR 双时间核对落点。"""
        self.userA.preset_playing('speaker')
        self.userA.seek_to(SEEK_RATIO, action='plus')

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
