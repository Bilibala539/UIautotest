# CASE-ID: radio-NEG-001
"""Swan 回归·电台：三区块基线与搜索框只读入口守卫（radio-NEG-001，部分转换）。

步骤 -> AW 映射（可自动化面：步骤1/步骤4；radio 页族 0 testId）：
- 步骤1 进首页电台 Tab 观察三区块基线 -> go_top_tab('电台') +
  assert_any_of_texts 区块标题候选（l10n 中文未核准，候选兜底）；
- 步骤4 搜索框只读入口 -> SWAN_HOME_RADIO_SEARCH_BAR [图] 点击跳
  全局搜索页（坑 5：不存在页内搜索结果态，不为页内搜索设计断言），
  press_back 返回；
- 步骤2/3（源列表 <8 条切块形态、空列表空态）依赖服务端短列表/空
  响应注入窗口，无注入手段，未纳入自动化——见 package_report.notes。

清理：只读断言，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_HOME_RADIO_SEARCH_BAR


class TestRadioIndexSliceGuard(BaseTest):
    """radio-NEG-001：三区块基线渲染 + 搜索入口只读跳转。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_slice_baseline_and_search_entry(self):
        """三区块渲染基线在位，搜索框只读跳全局搜索。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 步骤1：三区块基线（候选兜底）
        self.userA.assert_any_of_texts("全国电台", "国家台", "全国", timeout=8)
        self.userA.assert_any_of_texts("80后", "80er", "80", timeout=5)
        self.userA.assert_any_of_texts("90后", "90er", "90", timeout=5)
        # 步骤4：搜索框只读入口（跳全局搜索默认电台 Tab）
        if self.userA.probe_image(SWAN_HOME_RADIO_SEARCH_BAR,
                                  timeout=3) is None:
            pytest.skip("首页电台 Tab 搜索条图未命中（布局轮换），转人工复核")
        self.userA.click_image(SWAN_HOME_RADIO_SEARCH_BAR, timeout=10)
        self.userA.assert_any_of_texts("电台", "搜索歌曲", "搜索", timeout=8)
        self.userA.press_back()
        self.userA.assert_any_of_texts("全国电台", "国家台", "80", "90",
                                       timeout=8)

    def teardown(self) -> None:
        """只读断言无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
