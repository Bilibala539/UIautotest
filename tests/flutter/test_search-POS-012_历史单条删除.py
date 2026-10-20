# CASE-ID: search-POS-012
"""Swan 回归·搜索：搜索历史单条删除(search-POS-012)。

步骤→AW 映射：
- 补历史前置：自建两条历史 → search('ocean', entry='home') → press_back
  ×2（退回首页）→ search('tide', entry='home') → press_back（回历史态）
- 断言历史含两词 → text_exists('ocean') + text_exists('tide')
- 进删除模式 → enter_search_history_delete_mode()（mixin OCR '删除' 入口；
  入口为无文案图标时断言信息直指 template_needs 缺口）
- 删除 tide → click_text('tide') + text_not_exists('tide')
- 退出删除模式 → click_text('完成')，断言 ocean 保留 → text_exists('ocean')

⚠️ 注记：前置历史为用例自建（YAML 前置"已有 2 条历史"以现造承载）。
cleanup：无（历史数据随冷启动复位语义可接受）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestHistorySingleDelete(SwanRP03Mixin, BaseTest):
    """删除模式下单删 tide，ocean 保留。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_single_delete(self):
        """自建两条历史 → 删除模式删 tide → ocean 保留。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.search('ocean', entry='home')
        self.userA.press_back()
        self.userA.press_back()
        self.userA.search('tide', entry='home')
        self.userA.press_back()

        self.userA.text_exists('ocean', timeout=5)
        self.userA.text_exists('tide', timeout=5)

        self.userA.enter_search_history_delete_mode()
        self.userA.click_text('tide', timeout=5)
        self.userA.text_not_exists('tide', timeout=5)
        self.userA.click_text('完成', timeout=5)
        self.userA.text_exists('ocean', timeout=5)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索历史态（余 ocean 一条）
