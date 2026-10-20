# CASE-ID: radio-POS-007
"""Swan 回归·电台：首页电台 Tab 平台授权门正向通过（radio-POS-007）。

步骤 -> AW 映射（ensureHomePlatformAuthorized(terraceType) 正向面，
坑 14：Tab 有门、Hub 无门）：
- 步骤1 已授权账号进入首页电台 Tab -> ensure_logged_in_on_home +
  go_top_tab('电台')，直进无授权阻断弹层（弹层文案候选探测，
  命中按 SKIP-AUTH 口径运行时 skip 转授权预置）；
- 步骤2 断言 Tab 内容区正常渲染 -> assert_any_of_texts 三区块标题
  候选（授权门不误拦已授权态）。

清理：只读断言，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRadioTabAuthGatePass(BaseTest):
    """radio-POS-007：已授权态授权门正向通过，内容直进。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_tab_auth_gate_pass(self):
        """已授权账号直进电台 Tab，三区块渲染无阻断。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1：授权弹层阻断探测（未授权账号 SKIP-AUTH 口径）
        if (self.userA.find_text_by_ocr("授权通知", timeout=2) is not None
                or self.userA.find_text_by_ocr("去授权",
                                               timeout=1) is not None):
            pytest.skip("出现平台授权弹层（账号未授权，SKIP-AUTH），转授权预置")
        # 步骤2：三区块内容渲染（授权门不误拦）
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=8)

    def teardown(self) -> None:
        """只读断言无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
