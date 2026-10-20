# CASE-ID: vision-POS-001
# LINKED-CASE: vision-POS-001
"""Swan 回归·M10 可视音箱 Vision：MG100 设备 Vision 配置入口可达（vision-POS-001）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 设备页定位 MG100 设备卡 → ensure_logged_in_on_home + go_bottom_tab('设备')
  + text_exists('MG100')（测试设备名 TESTDEV-MG100-01 子串命中）
- S2-S3 点击设备卡 → Vision 配置入口 → 落地壁纸主页面
  → open_vision_wallpaper_from_device（OCR「MG100」→「Vision」→ 落地锚）
- S4 快照加载完成渲染 → 落地断言即收口（getVisionData 渲染后锚点才稳定出现）
前置：名下已绑定 MG100 TESTDEV-MG100-01 在线（需人工预置专用设备，接入测试
WLAN）；未绑定态 Vision 域无任何入口（knowledge/swan/pages/swan_Vision域不可达页.md）。
清理：只读冒烟；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionEntryReachable(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """MG100 设备 Vision 配置入口可达（vision-POS-001）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_vision_entry_reachable(self):
        """设备页 MG100 卡 → Vision 配置入口 → 壁纸主页面渲染。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab('设备')
        # S1 设备页定位 MG100 设备卡（设备卡可见）
        self.userA.text_exists('MG100', timeout=15)
        # S2-S3 点击进入 → Vision 配置入口 → 落地壁纸主页面（双 pager 区域）
        self.userA.open_vision_wallpaper_from_device()
        # S4 落地断言已收口快照渲染（无白屏无崩溃由锚点稳定出现表达）

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
