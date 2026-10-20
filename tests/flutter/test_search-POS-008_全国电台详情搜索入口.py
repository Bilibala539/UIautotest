# CASE-ID: search-POS-008
"""Swan 回归·搜索：全国电台详情搜索入口进搜索页(search-POS-008,B 级)。

步骤→AW 映射（电台详情页知识库未探索——按 ADD1 口径页面未探索归 B，
照常产出 OCR 优先 py，缺口登记 template_needs）：
- 前置：授权探针（网易云行未授权态 [图]，同既有平台内容页用例口径）→
  未授权 skip（电台内容有授权门禁）
- 进电台 Tab 全国区块 → go_top_tab('电台') + text_exists('全国电台')
- 点任一电台卡进详情 → tap_first_row_below_anchor('全国电台')（区块头
  下方首个 OCR 行=电台卡，动态定位）
- 详情页搜索入口 → find_text_by_ocr('搜索') 探测 + click_text('搜索')
  （入口无锚图，template_needs 已登记 fm 电台详情页搜索入口）
- 断言落搜索页历史输入态 → text_exists('搜索歌曲或艺术家等') +
  text_exists('搜索历史')（输入框与历史区渲染正常）
- 收尾 → press_back ×2 退回电台 Tab（锚断言）

cleanup：只读冒烟，teardown body 一律 pass（冷启动复位）。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestCountryRadioDetailSearchEntry(SwanRP03Mixin, BaseTest):
    """全国电台详情页搜索入口可达搜索页（历史输入态）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_country_radio_detail_search_entry(self):
        """全国区块电台卡 → 详情 → 搜索入口 → 搜索页渲染正常。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab('平台')
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                 timeout=3) is not None:
            pytest.skip("账号未授权平台（网易云行未授权态 [图] 命中）——"
                        "电台内容有授权门禁；授权后自动恢复")
        self.userA.go_bottom_tab('首页')

        self.userA.go_top_tab('电台')
        self.userA.text_exists('全国电台', timeout=15)
        self.userA.tap_first_row_below_anchor('全国电台')

        assert self.userA.find_text_by_ocr('搜索', timeout=5) is not None, (
            "电台详情页未探测到搜索入口（OCR '搜索' 未命中）——页面未探索，"
            "template_needs 已登记 fm 电台详情页搜索入口锚图")
        self.userA.click_text('搜索', timeout=5)
        self.userA.text_exists('搜索歌曲或艺术家等', timeout=10)
        self.userA.text_exists('搜索历史', timeout=5)

        self.userA.press_back()
        self.userA.press_back()
        self.userA.text_exists('全国电台', timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在电台 Tab
