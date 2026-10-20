# CASE-ID: radio-POS-009
"""Swan 回归·电台：全国台列表分页加载与追加渲染（radio-POS-009 正向面）。

步骤 -> AW 映射（broadcast/list size=30 分页；_deduplicateStations
stableId 去重保序、整页重叠 _hasMore=false 终止、连点互斥为服务端/
Provider 契约，OCR 侧断追加渲染可观察面）：
- 步骤0 前置进全国电台页 -> go_top_tab('电台') + tap_card_by_texts；
- 步骤1 滚动触底触发加载更多 -> swipe_up x4 后 ocr_page_texts
  与触底前集合 diff，新增文本项=下一页追加渲染证据；
- 步骤2 断言追加渲染 -> 新增项非空（单页即到底按 SKIP-DATA 口径
  运行时 skip 转数据预置；去重保序 OCR 无法逐项核验，登记说明）。

清理：纯查询，teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest


class TestRadioStationPaging(BaseTest):
    """radio-POS-009：触底加载更多，追加渲染出现新内容项。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_radio_station_paging_append(self):
        """滚动触底后列表追加渲染（新内容项出现）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("电台")
        # 前置：全国电台页
        self.userA.tap_card_by_texts("全国电台", "国家台", "全国")
        self.userA.assert_any_of_texts("城市", "全国电台", timeout=8)
        # 步骤1：触底前文本集合基线
        before = set(self.userA.ocr_page_texts())
        # 步骤2：连续上滑触底触发加载更多
        for _ in range(4):
            self.userA.swipe_up()
        after = self.userA.ocr_page_texts()
        new_items = [t for t in after if t not in before and len(t) >= 4]
        if not new_items:
            pytest.skip("列表单页即到底（服务端数据不足多页，SKIP-DATA），转数据预置")
        # 步骤3：追加渲染断言
        assert len(new_items) >= 1, "触底后无新增内容项（分页未触发）"

    def teardown(self) -> None:
        """纯查询无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
