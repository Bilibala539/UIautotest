# CASE-ID: vision-NEG-003
# LINKED-CASE: vision-NEG-003
"""Swan 回归·M10 可视音箱 Vision：语音包试听中退出——异步起播守卫（vision-NEG-003）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_voice_pack_page
- S1 点击语音包行触发选中+试听 → pick_voice_pack_row()（整行点击=选中+试听，
  行锚=KB 实测系统角色名候选；「试听 1s 内」时序窗口内完成点击即返回）
- S2 试听 1s 内立即返回退出 → press_back + 上级页锚 assert_any_text
  （守卫生效的可观测面：退出顺畅无卡死无黑屏；_voicePlaybackGeneration
  守卫的「已退出页面不异步起播」内部时序不可 OCR 观测，残留播放态强断言
  待标定——见 package_report.template_needs）
- S3 重进复核页面状态干净 → open_vision_voice_pack_page + pick_voice_pack_row
  复命中（列表可正常交互=无残留阻塞；播放态标识未标定）
前置：语音包页可达且有可试听项（合成音源就绪）。
清理：只读+试听不保存（整行点击选中态不落库，禁区 2 安全）；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVoicePackExitGuard(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """语音包试听中退出——异步起播守卫（vision-NEG-003）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_voice_pack_exit_during_audition(self):
        """试听中立即退出守卫生效：退出顺畅、重进页面状态干净。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        # S1 整行点击语音包行触发选中+试听（行锚=系统角色名候选）
        self.userA.open_vision_voice_pack_page()
        self.userA.pick_voice_pack_row()
        # S2 试听 1s 内立即返回退出（守卫生效——退出顺畅无卡死）
        self.userA.press_back()
        self.userA.assert_any_text(('角色', '音色', '语音包', 'Vision'), timeout=10)
        # S3 重进复核页面状态干净（列表可正常交互）
        self.userA.open_vision_voice_pack_page()
        self.userA.pick_voice_pack_row()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
