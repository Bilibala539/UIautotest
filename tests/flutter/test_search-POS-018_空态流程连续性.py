# CASE-ID: search-POS-018
"""Swan 回归·搜索：空态后流程连续可恢复(search-POS-018)。

步骤→AW 映射：
- 无结果词搜索 → search('zzqxv', entry='home') +
  assert_search_results('单曲', [], allow_empty=True)（空态显式断言）
- 空态返回不退出 → press_back + text_exists('搜索歌曲或艺术家等')（回
  历史态锚）→ press_back + assert_on_home()
- 正常词恢复搜索 → search('ocean', entry='home')，页面功能正常：
  平台列表（环境变量 SWAN_SEARCH_PLATFORMS）非空时断言各平台分组渲染；
  未配置（未授权账号）时断言空态一致呈现——与账号状态行为一致即"连续"

cleanup：无用例私有清理（冷启动模型）。
"""
from __future__ import annotations

import os

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestEmptyStateFlowContinuity(SwanRP03Mixin, BaseTest):
    """空态→返回→恢复首页→再搜索，流程连续无卡死。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_empty_state_flow_continuity(self):
        """空态搜索 → 返回退出 → 正常词再搜可正常呈现。"""
        self.userA.ensure_logged_in_on_home()

        self.userA.search('zzqxv', entry='home')
        self.userA.assert_search_results('单曲', [], allow_empty=True)
        self.userA.press_back()
        self.userA.text_exists('搜索歌曲或艺术家等', timeout=5)
        self.userA.press_back()
        self.userA.assert_on_home()

        platforms = [p.strip() for p in
                     os.environ.get("SWAN_SEARCH_PLATFORMS", "").split(",")
                     if p.strip()]
        self.userA.search('ocean', entry='home')
        if platforms:
            self.userA.assert_search_results('单曲', platforms,
                                             allow_empty=False)
        else:
            self.userA.assert_search_results('单曲', [], allow_empty=True)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索结果页
