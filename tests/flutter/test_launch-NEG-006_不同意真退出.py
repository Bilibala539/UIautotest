# CASE-ID: launch-NEG-006
"""Swan 回归·M01 启动与隐私：隐私不同意真退出 App（launch-NEG-006）。

用例 → AW 映射：
- 冷启动至隐私弹层 → 夹具冷启动 + privacy_dialog_visible() 探测
- 点击不同意 → click_text("不同意")（exitApp 真退出触发）
- 进程退出取证 → assert_app_exited(package)（dumpsys 前台包名轮询至
  异于 App 包名——进程级证据，非 UI 面断言）
- 重启后未同意保持 → relaunch_app(package) + privacy_dialog_visible() 断言
不可观测面声明：exitApp 三端语义差异（iOS/OHOS 卡未决 1）不在本
Android 口径内；「真退出而非页面返回」由前台包名证据承载——若仅为
页面返回，前台包名仍为 App 包名，断言即失败。
状态条件：一次性会话——需全新安装未同意态窗口（privacyRequired）；
135 常态已同意，弹层不可见即 skip（同 test_launch-NEG-001 条件用例
口径）。烧毁的未同意态由 teardown 代点同意恢复，不毁执行现场。
清理（YAML cleanup「需人工恢复设备态」的自动化口径）：teardown 点击
「同意」恢复同意态，供后续用例衔接。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchNeg006DisagreeExitsApp(SwanRP01Mixin, BaseTest):
    """隐私不同意真退出 App（launch-NEG-006）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_disagree_exits_app(self):
        """点击「不同意」真退出 App（进程终止），重启后隐私态保持未同意。"""
        if not self.userA.privacy_dialog_visible(timeout=3):
            pytest.skip("隐私弹层不可见（账号已同意态）——需全新安装未同意窗口")
        self.userA.click_text("不同意", timeout=10)
        self.userA.assert_app_exited(self.userA.package)
        self.userA.relaunch_app(self.userA.package)
        assert self.userA.privacy_dialog_visible(timeout=10), (
            "重启后隐私弹层未重现（不同意被误写为已同意或弹层被自动处置）")

    def teardown(self) -> None:
        """用例私有清理（YAML cleanup）：点击「同意」恢复同意态。"""
        if self.userA.privacy_dialog_visible(timeout=2):
            self.userA.accept_privacy_dialog()
