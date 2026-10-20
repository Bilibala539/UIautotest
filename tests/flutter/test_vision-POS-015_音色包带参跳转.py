# CASE-ID: vision-POS-015
# LINKED-CASE: vision-POS-015
"""Swan 回归·M10 可视音箱 Vision：角色卡音色包入口带参跳转（vision-POS-015）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 点击角色卡音色包入口 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_ai_roles_page + click_text('音色')（vision-ai-role-voice-pack
  入口锚）→ 语音包页落地断言
- S2 当前选中音色行高亮 → assert_any_text（「使用中/已选择/当前」候选，
  selectedVoiceId 透传正向；行条目文案未标定见 package_report.template_needs）
- S3 返回角色页 → press_back + text_exists('角色')
前置：Vision AI 角色页至少 1 个系统角色可点；已绑定 MG100。
清理：只读跳转零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionVoicePackEntry(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """角色卡音色包入口带参跳转（vision-POS-015）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_voice_pack_entry_with_args(self):
        """音色包入口 → 语音包页落地（带参正向）、选中态锚点命中；返回角色页。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_ai_roles_page()
        # S1 点击角色卡的音色包入口 → 语音包页落地
        self.userA.click_text('音色', timeout=10)
        self.userA.assert_any_text(('语音包', '音色'), timeout=10)
        # S2 当前选中音色行高亮（selectedVoiceId 透传）
        self.userA.assert_any_text(('使用中', '已选择', '当前'), timeout=10)
        # S3 返回角色页
        self.userA.press_back()
        self.userA.text_exists('角色', timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
