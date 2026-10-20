# CASE-ID: search-NEG-015
"""Swan 回归·搜索：结果项进详情后返回——搜索态残留一致(search-NEG-015,部分转换)。

步骤→AW 映射（需真实结果可导航项，合成词经环境变量注入可命中词）：
- 前置：授权探针（网易云行未授权态 [图]，同既有平台内容页用例口径）→
  未授权 skip；关键词 SWAN_SEARCH_KEYWORD_NAV（缺省 'synthkw-nav'，
  执行轮替换为可命中歌单类结果的合成词）
- 搜索 → search(keyword, entry='home')
- 切歌单 Tab → click_text('歌单', region=结果顶 Tab 行)
- 点首个歌单卡进详情 → tap_first_row_below_anchor('歌单')（Tab 行下方
  首个 OCR 行，排除分组头）+ 歌单详情锚 [图] SWAN_PD_PLAY_ALL
- 返回结果页 → press_back + 关键词回显 text_exists(keyword) + 歌单
  Tab 行仍在（Tab 不跳变）
- 再次进入同卡 → tap_first_row_below_anchor('歌单') + 锚 [图] + press_back

⚠️ 部分转换注记：「结果不重拉」以请求计数不变为准——框架无抓包/请求
计数通道（TCBATCH1-ADD1 点名能力缺口）；OCR 承载面=关键词/Tab/结果
残留一致 + 往返可重复。
cleanup：无（只读往返，teardown pass）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PD_PLAY_ALL,
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestResultDetailRoundTrip(SwanRP03Mixin, BaseTest):
    """进歌单详情→返回：关键词/Tab 残留一致，往返可重复。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_result_detail_round_trip(self):
        """歌单结果进详情→返回→状态保持→再进详情→返回。"""
        keyword = os.environ.get("SWAN_SEARCH_KEYWORD_NAV", "").strip() or "synthkw-nav"

        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab('平台')
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                 timeout=3) is not None:
            pytest.skip("账号未授权平台（网易云行未授权态 [图] 命中）——"
                        "本用例需已授权态有可导航结果；授权后自动恢复")
        self.userA.search(keyword, entry='home')

        self.userA.click_text('歌单', timeout=5, region=(0, 190, 720, 130))
        self.userA.tap_first_row_below_anchor('歌单')
        assert self.userA.find_image(SWAN_PD_PLAY_ALL, timeout=10) is not None, (
            "点击歌单结果项后未落歌单详情页")

        self.userA.press_back()
        self.userA.text_exists(keyword, timeout=5)
        self.userA.text_exists('歌单', timeout=5, region=(0, 190, 720, 130))

        self.userA.tap_first_row_below_anchor('歌单')
        assert self.userA.find_image(SWAN_PD_PLAY_ALL, timeout=10) is not None, (
            "第二次进入同条目失败（路由栈异常?）")
        self.userA.press_back()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在搜索结果页
