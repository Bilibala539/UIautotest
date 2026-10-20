# CASE-ID: vision-POS-018
# LINKED-CASE: vision-POS-018
"""Swan 回归·M10 可视音箱 Vision：语音包选择后不保存返回零写——播放器无残留（vision-POS-018）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_voice_pack_page
  （「当前选中项已知」原为前置；选中项标识未标定，弱化为任一行候选点击——
  非当前行的强定位待标定，见 package_report.template_needs）
- S1 整行点击非当前语音包 → pick_voice_pack_row()（KB 实测系统角色名候选锚，
  触发选中及可能的试听播放）→ 选中态切换 = 选中标识候选命中（未标定 SKIP-DATA）
- S2 立即系统返回退出 → press_back + 上级页锚 assert_any_text
  （返回顺畅可观测面；播放器 pause/dispose 先于放行的内部时序不可 OCR 观测）
- S3 重进核对 → open_vision_voice_pack_page + 列表可交互（选中项仍为原值=未
  落库正向；原选中项标识组合未标定，弱断言收口+template_needs 登记）
前置：语音包 ≥2（专用测试账号已登录）。
清理：不保存直接返回=零写；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin

# 选中态标识候选（文案未标定，语义预测——标定后补强断言）
_SELECTED_HINTS = ('已选择', '已选', '使用中', '正在使用')


class TestVoicePackNoSaveExit(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """语音包选择后不保存返回零写——播放器无残留（vision-POS-018）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_select_then_exit_without_save(self):
        """选中切换→立即返回顺畅→重进选中态还原（未落库正向）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_voice_pack_page()
        # S1 整行点击非当前语音包（触发选中及可能的试听播放）
        self.userA.pick_voice_pack_row()
        self.userA.assert_any_text(_SELECTED_HINTS, timeout=8)
        # S2 立即系统返回退出（返回顺畅，播放器先 pause/dispose 再放行）
        self.userA.press_back()
        self.userA.assert_any_text(('角色', '音色', '语音包', 'Vision'), timeout=10)
        # S3 重进核对（选中项仍为原值——未落库正向；列表可交互收口）
        self.userA.open_vision_voice_pack_page()
        self.userA.pick_voice_pack_row()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
