# CASE-ID: vision-POS-017
# LINKED-CASE: vision-POS-017
"""Swan 回归·M10 可视音箱 Vision：语音包整行点击选中——无独立试听热区契约正向（vision-POS-017）。

用例 → AW 映射（P06 包 mixin OCR 文本锚）：
- 前置 → ensure_logged_in_on_home + go_top_tab('可视音箱') + open_vision_voice_pack_page
- S1 断言无独立试听热区 → text_not_exists('试听')（OCR 层：行内无「试听」
  按钮文案=热区并入整行的可观测面；图形热区形态未标定见 template_needs）
- S2 整行点击语音包 B → pick_voice_pack_row()（KB 实测系统角色名候选锚，
  整行点击=选中+试听）→ 选中态迁移 = 选中标识候选 assert_any_text 命中
  （标识文案未标定，候选全缺判 SKIP-DATA）
- S3 不点保存直接返回 → press_back + 重进（vision_voice_pack_save 保存=写+
  设备同步——禁区 2，本用例止步选择态；「重进选中态还原」强断言依赖原选中
  项+标识组合定位，未标定——弱断言收口+template_needs 登记）
前置：语音包 ≥2（专用测试账号已登录）。
清理：不保存直接返回=零写零同步；teardown 冷启动模型 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanPlayerRegressionMixin
from utils.aw.business.swan_r_p06 import SwanRP06Mixin

# 选中态标识候选（文案未标定，语义预测——标定后补强断言）
_SELECTED_HINTS = ('已选择', '已选', '使用中', '正在使用')


class TestVoicePackRowSelect(SwanRP06Mixin, SwanPlayerRegressionMixin, BaseTest):
    """语音包整行点击选中——无独立试听热区契约正向（vision-POS-017）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_whole_row_click_selects(self):
        """无独立试听热区→整行点击选中迁移→不保存返回零写。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab('可视音箱')
        self.userA.open_vision_voice_pack_page()
        # S1 行内无独立试听预览热区（OCR 层无「试听」按钮文案）
        self.userA.text_not_exists('试听', timeout=8)
        # S2 整行点击语音包 B → 选中态迁移（标识候选命中）
        self.userA.pick_voice_pack_row()
        marker = self.userA.assert_any_text(_SELECTED_HINTS, timeout=8)
        # S3 不点保存直接返回，重进还原（零保存零同步）
        self.userA.press_back()
        self.userA.open_vision_voice_pack_page()
        self.userA.text_exists(marker, timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
