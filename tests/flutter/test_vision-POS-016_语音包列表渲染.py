# CASE-ID: vision-POS-016
# LINKED-CASE: vision-POS-016
"""Swan 回归·M10 可视音箱 Vision：语音包列表完整渲染与选中高亮（vision-POS-016）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入语音包页 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_voice_pack_page
- S2 滚动浏览语音包行 → swipe_up（滚动无卡顿以顺畅返回表达；
  行条目文案未标定，模板需求见 package_report.template_needs）
- S3 当前选中项高亮 → assert_any_text（「使用中/已选择/当前」候选；
  selectedVoiceId 为 -1 或缺省时的默认态按实际 UI 记录）
- 退出 → press_back（只读）
前置：已绑定 MG100 TESTDEV-MG100-01 在线；语音包列表非空。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionVoicePackList(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """语音包列表完整渲染与选中高亮（vision-POS-016）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_voice_pack_list_rendered(self):
        """语音包页落地、滚动浏览顺畅、选中态锚点命中；退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_voice_pack_page()
        # S2 滚动浏览语音包行
        self.userA.swipe_up()
        # S3 当前选中项高亮
        self.userA.assert_any_text(('使用中', '已选择', '当前'), timeout=10)
        # 退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
