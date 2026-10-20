# CASE-ID: home-POS-009
"""Swan 回归·首页：已授权平台区块两路直达(home-POS-009)。

步骤→AW 映射：
- 前置：账号已授权平台（授权态代理探针=平台页网易云行未授权态 [图]，
  与既有平台内容页用例同口径；未授权 → pytest.skip，授权后自动恢复）
- 路一：音乐 Tab 平台区块头直达 → go_top_tab('音乐') + click_text(
  '网易云音乐') + 平台主页锚 [OCR] text_exists('搜索网易云音乐')
- 路二：返回音乐 Tab 点击同平台歌单卡 → press_back + mixin
  tap_first_row_below_anchor('网易云音乐')（区块头下方首个 OCR 行=歌单卡，
  动态定位）+ 歌单详情锚 [图] SWAN_PD_PLAY_ALL
- 断言回音乐 Tab 原位 → press_back + text_exists('QQ音乐')

cleanup：歌单详情/平台主页均为 push 页，步骤内已逐级 press_back 退回；
teardown body 一律 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PD_PLAY_ALL,
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
)
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestAuthorizedPlatformDirectEntry(SwanRP03Mixin, BaseTest):
    """已授权平台：区块头直达平台主页、歌单卡直达歌单详情。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_authorized_platform_direct_entries(self):
        """网易云区块头直达平台主页；歌单卡直达歌单详情。"""
        self.userA.ensure_logged_in_on_home()
        # 账号授权态探针（代理口径同既有平台内容页用例）
        self.userA.go_bottom_tab('平台')
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                 timeout=3) is not None:
            pytest.skip("账号未授权平台（网易云行未授权态 [图] 命中）——"
                        "本用例需已授权态；授权后自动恢复运行")
        self.userA.go_bottom_tab('首页')

        # 路一：区块头直达平台主页
        self.userA.go_top_tab('音乐')
        if self.userA.find_text_by_ocr('网易云音乐', timeout=2) is None:
            self.userA.swipe_up()
        self.userA.click_text('网易云音乐', timeout=10)
        self.userA.text_exists('搜索网易云音乐', timeout=15)

        # 路二：返回后点同平台歌单卡进歌单详情
        self.userA.press_back()
        self.userA.tap_first_row_below_anchor('网易云音乐')
        assert self.userA.find_image(SWAN_PD_PLAY_ALL, timeout=10) is not None, (
            "点击歌单卡后播放全部锚 [图] 未命中——未落歌单详情页")
        self.userA.press_back()
        self.userA.text_exists('QQ音乐', timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在音乐 Tab（push 页已在步骤内逐级退回）
