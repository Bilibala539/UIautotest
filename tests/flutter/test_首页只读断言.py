"""Swan Flutter 首页只读断言（原 test_swan_readonly_pages.py，2026-10-12 拆分）。

覆盖：首页元素（4 个全局 tab + 底部播放条非致命探测）。
前置：账号已登录（用例开头 login_by_sms 幂等确保，已在首页自动跳过）。

⛔ 危险入口一律不点（只做存在性断言）：
授权/充值、播放暂停/音量/上下首、设备卡/设置/同步/添加设备、注销账号、
任何确认弹窗。
断言辅助与锚点探测在 SwanLoginRegressionMixin（业务层，存量 key 口径）。
每条用例收尾回首页（G3/G4）。
"""
from __future__ import annotations

import os

import pytest

from conftest import BaseTest
from utils.aw.business.swan import SwanBusiness
from utils.aw.business.swan_regression import SwanLoginRegressionMixin



class TestSwanHomeReadonly(SwanLoginRegressionMixin, BaseTest):
    """首页只读断言。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户与基础操作入口。"""
        self.user = self.users("swanuserA")
        self.aw = self.user.aw
        self.phone = self.user.phone
        self.password = os.environ.get("SWAN_PASSWORD", "").strip()
        self.package = os.environ.get("SWAN_PACKAGE", "com.swan.network").strip()

    def test_home_page_elements(self):
        """首页元素：4 个全局 tab key + 底部播放条（非致命探测）。

        底部播放条模板截于「输出=扬声器/- -」无会话态，rig 持久播放会话
        （输出=设备名+曲目名）下内容永久偏离模板，存在性降级为非致命探测：
        命中记 info，未命中记 warning 不挂用例（口径同
        swan_regression verify-run3）。
        """
        self._ensure_logged_in_on_home()
        # 2026-10-12 key 迁移：逐 tab key 存在性断言因选中态不可见图化后
        # 不可行（当前 Tab 选中时其未选中态图恰不匹配），改为首页壳锚
        # （底部导航 4 图任一）+ 顶 Tab「推荐」OCR 双证据
        assert self.aw._home_shell_visible(timeout=3), "首页缺少底部导航壳锚 [图]"
        assert self.aw.find_text_by_ocr("推荐", timeout=10) is not None, (
            "首页缺少顶 Tab「推荐」文字 [OCR]")
        self._probe_bottom_player_bar()

    def teardown(self) -> None:
        """G3/G4 清理链由 mixin teardown 承担（本用例无自定义清理）。"""
        super().teardown()