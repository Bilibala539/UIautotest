# CASE-ID: aw-搜索_home_艺人
# LINKED-CASE: search-POS-016,search-POS-020,search-POS-021
"""Swan 回归·搜索域：关键词搜索与结果分类（回归用例 69-72）。

用例 -> AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域8）：
- 用例69-72 搜索并核对结果分类矩阵 -> search(keyword, entry)
  + assert_search_results('艺人', platforms)

矩阵：entry（home=音乐 Tab 搜索条 / radio=电台 Tab 搜索条——功能地图 8 处
入口中仅这两处真机验证过，平台域入口 KB 未验证暂不支持）× tab（结果页
六分类，方案口径「博客」归一为页内文案「播客」）。
关键词默认 piano（英文，adb 输入实测可达；中文待 IME 方案，框架层待用户
决策），可按分类用 SWAN_SEARCH_KEYWORD_<tab> 覆盖。
数据口径（知识库 Wave4 实测）：未授权账号结果恒为空态「没有找到相关结果」，
SWAN_SEARCH_PLATFORMS 未配置时按空态断言（SWAN_SEARCH_EMPTY [图]）；
已授权账号配置该变量后改按结果区平台名断言。run4 真机补充（qq/netease
授权 + piano）：电台 Tab 结果区空态、播客 Tab 有结果——电台内容源不按
关键词返回结果，授权口径下电台 Tab 降级为「空态或有结果均可」（见
SwanBusiness.assert_search_results allow_empty 注），域内「有搜索能力」
由其余 5 个 Tab 的「有结果」断言承担。
清理（G3/G4）：teardown 退出搜索 push 页回首页。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan_regression import SwanContentRegressionMixin


class TestSearch(SwanContentRegressionMixin, BaseTest):
    """关键词搜索与结果分类（回归用例 69-72）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_search_results_by_tab(self):
        """用例69-72：按分类搜索并断言结果区（空态或平台名）。

        run4 实测口径（见模块 docstring）：授权平台下电台 Tab 空态/有结果
        均可接受（allow_empty），其余 Tab 维持「有结果」硬断言。"""
        keyword = (os.environ.get("SWAN_SEARCH_KEYWORD_艺人", "").strip()
                   or "piano")
        platforms = [p.strip() for p in
                     os.environ.get("SWAN_SEARCH_PLATFORMS", "").split(",")
                     if p.strip()]
        self.userA.ensure_logged_in_on_home()
        self.userA.search(keyword, entry='home')
        self.userA.assert_search_results(
            '艺人', platforms,
            allow_empty=False)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
