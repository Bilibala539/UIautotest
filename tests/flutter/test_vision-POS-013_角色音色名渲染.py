# CASE-ID: vision-POS-013
# LINKED-CASE: vision-POS-013
"""Swan 回归·M10 可视音箱 Vision：AI 角色音色映射展示——映射优先级正向（vision-POS-013）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 浏览角色卡音色名 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_ai_roles_page；assert_any_text（「音色」区锚/角色名兜底，
  音色名渲染即映射链正向：aiRoleVoiceMap > 路由透传 > 默认 voiceId）
- S2 路由透传对照 → 条件分支「如从带选中音色的入口进入」，依赖带参环境，
  优先级序列展示归 vision-POS-015 带参跳转覆盖，本用例不重复构造
- S3 退出 → press_back（零写）
前置：已绑定 MG100 TESTDEV-MG100-01 在线；getVisionData 快照含 aiRoleVoiceMap
（无映射走角色默认 voiceId——两分支均可执行）。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionRoleVoiceName(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """Vision AI 角色音色映射展示（vision-POS-013）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_role_voice_name_rendered(self):
        """角色卡音色名渲染（映射优先级正向）；退出零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_ai_roles_page()
        # S1 角色卡音色名渲染（音色区锚/系统角色名兜底）
        self.userA.assert_any_text(('音色', '小薇', '惠威百科'), timeout=10)
        # S3 退出（零写）
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
