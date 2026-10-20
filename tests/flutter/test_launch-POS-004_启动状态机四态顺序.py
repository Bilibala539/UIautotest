# CASE-ID: launch-POS-004
"""Swan 回归·M01 启动与隐私：启动状态机四态顺序推进（launch-POS-004）。

用例 → AW 映射：
- 冷启动至隐私必答态 → 夹具冷启动 + privacy_dialog_visible() 断言
  （privacyRequired：登录页+隐私弹层叠加呈现）
- 点击同意 → accept_privacy_dialog()（privacyRequired→loginRequired
  转移，内含弹层关闭断言）
- 登录必答态呈现 → assert_on_login_page()（登录页锚 [图]，状态机推进
  终态落点证据）
不可观测面声明：启动图（initializing）阶段与「无跳变无回退」的日志级
取证（启动日志锚点）不在 UI 面——夹具冷启动后启动图阶段已耗尽，运行期
不可再观测；启动图锚点已登记 template_needs，截取后可于 force-stop
冷启动序列升级先行性探测。privacyRequired→loginRequired 两态呈现与
转移以可观察序列收口（未同意弹层先行呈现→同意→登录页落点）。
状态条件：需全新安装未同意态窗口（privacyRequired）；135 常态已同意，
弹层不可见即 skip（同 test_launch-NEG-001 条件用例口径）。
清理（YAML cleanup）：无——同意态为自然衔接态。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestLaunchPos004StartupStateMachine(SwanRP01Mixin, BaseTest):
    """启动状态机四态顺序推进（launch-POS-004）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_startup_state_machine_order(self):
        """privacyRequired→loginRequired 按序推进，落点登录必答态。"""
        if not self.userA.privacy_dialog_visible(timeout=3):
            pytest.skip("隐私弹层不可见（账号已同意态）——需全新安装未同意窗口")
        self.userA.accept_privacy_dialog()
        self.userA.assert_on_login_page()

    def teardown(self) -> None:
        """无用例私有清理（同意态为自然衔接态，冷启动模型复位）。"""
        pass
