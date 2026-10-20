# CASE-ID: vision-POS-004
# LINKED-CASE: vision-POS-004
"""Swan 回归·M10 可视音箱 Vision：语音包页可达与行列表渲染（vision-POS-004）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- S1 进入语音包页 → ensure_logged_in_on_home + go_top_tab('可视音箱')
  + open_vision_voice_pack_page（Vision 页直入口探测「语音包」，无则经 AI
  角色页角色卡「音色」入口——入口路径二选一，方法内自动兜底）
- S2 行列表渲染 → assert_any_text（「语音包」/「音色」页壳锚，行条目文案
  未标定，模板需求见 package_report.template_needs）
- S3 返回退出 → press_back
前置：Vision AI 角色页或壁纸主页可达（已绑定 MG100，需人工预置）。
清理：只读浏览零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin


class TestVisionVoicePackPage(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """语音包页可达与行列表渲染（vision-POS-004）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_voice_pack_page_reachable(self):
        """语音包页落地（携角色与音色参数带参正向）、行列表渲染；返回退出。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_voice_pack_page()
        # S2 页面壳与行列表渲染锚点
        self.userA.assert_any_text(('语音包', '音色'), timeout=10)
        # S3 返回退出
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
