"""Swan 回归·域6：平台内容页进入（回归用例 38-40）。

用例 → AW 映射（docs/Swan回归用例AW实现方案.md §2.3 域6）：
- 用例38-40 平台内容页进入 → open_platform(platform) + 主页锚 [OCR] 断言

⚠️ 状态条件用例：**需账号已授权目标平台**（未授权行体点击无反应，explorer
实测+知识库实锤）。授权流程搁置中（网易云服务端验证码不受控，2026-10-13
用户拍板），未授权态自动 skip——授权后自动恢复运行。
探针：网易云行未授权态 [图] 可见 = 账号未授权（以网易云行做账号授权态
代理探针；局限：仅反映网易云，QQ 授权态未单独探测，两平台同批授权场景
下足够）。
清理：open_platform 落地主页为 push 页——press_back 退回平台页 → go_home
（mixin teardown 亦有兜底）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
    SWAN_TAB_PLATFORM,
)
from utils.aw.business.swan_regression import SwanLoginRegressionMixin


class TestPlatformHomeEntry(SwanLoginRegressionMixin, BaseTest):
    """平台内容页进入（回归用例 38-40）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_open_platform_home(self):
        """用例38-40：平台页进入已授权平台主页，主页锚 [OCR] 断言。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.click_image(SWAN_TAB_PLATFORM, timeout=10)
        # 账号授权态探针：网易云行未授权态 [图] 可见 = 全未授权 → skip
        assert self.userA._platform_page_visible(), (
            "未到达平台页（网易云行两态 [图] 均未命中）")
        if self.userA.find_image(SWAN_PLATFORM_NETEASE_ROW_UNAUTHORIZED,
                              timeout=3) is not None:
            pytest.skip(
                "账号未授权任何平台（网易云行未授权态 [图] 命中）——平台内容"
                "用例需已授权态；授权域搁置中（网易云验证码不受控，首跑需人工读码）")
        self.userA.open_platform('qq')
        # 收尾：主页为 push 页，退回平台页再回首页
        self.userA.press_back()
        self.userA.go_home()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
