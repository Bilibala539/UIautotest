# CASE-ID: search-POS-006
"""Swan 回归·搜索：平台内容页搜索入口进搜索输入页(search-POS-006)。

步骤→AW 映射：
- 前置：账号已授权平台（授权态代理探针=平台页网易云行未授权态 [图]，
  同既有平台内容页用例口径；未授权 → pytest.skip，授权后自动恢复）
- 进 QQ 音乐平台主页 → open_platform('qq')（主页锚断言在方法内）
- 平台主页搜索框进输入页 → open_search_input_page(
  ocr_fallback='搜索QQ音乐')（OCR 兜底口径，_PLATFORM_HOME_SEARCH_TEXT
  同款文案；mixin 内含授权通知弹层处置 + 输入页 hint 到位断言）
- 收尾退回 → press_back + go_home

cleanup：平台主页为 push 页，步骤内已 press_back + go_home；
teardown body 一律 pass。
"""
from __future__ import annotations

import pytest

from conftest import BaseTest
from image.image_name_mapping import SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED
from utils.aw.business.swan_r_p03 import SwanRP03Mixin


class TestPlatformPageSearchEntry(SwanRP03Mixin, BaseTest):
    """QQ 音乐平台主页搜索框进入搜索输入页。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_platform_page_search_entry(self):
        """平台页 → QQ 音乐主页 → 搜索框 → 输入页 hint 到位 → 退回。"""
        self.userA.ensure_logged_in_on_home()
        # 账号授权态探针（代理口径同既有平台内容页用例）
        self.userA.go_bottom_tab('平台')
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                                 timeout=3) is not None:
            pytest.skip("账号未授权平台（网易云行未授权态 [图] 命中）——"
                        "本用例需已授权态；授权后自动恢复运行")

        self.userA.open_platform('qq')
        self.userA.open_search_input_page(ocr_fallback='搜索QQ音乐')

        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
        # 结束状态：已登录停在首页（push 页已退回）
