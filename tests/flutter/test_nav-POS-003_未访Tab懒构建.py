# CASE-ID: nav-POS-003
"""Swan 回归·M03 主框架导航：Tab 首次进入懒构建渲染正常（nav-POS-003）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()
- 依次切入未访 Tab（设备→我的）→ go_bottom_tab()（内部含落页锚点断言）
- 我的页首次构建渲染完整 → [图] SWAN_ME_ACCOUNT_ENTRY 账号入口存在断言
（首次构建的 shrink 占位/无越界请求为内部机制，UI 面以首切渲染完整
收口；懒构建语义由夹具冷启动保证「首次」——每条用例起点进程全新。）
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import SWAN_ME_ACCOUNT_ENTRY


class TestNavPos003LazyTabBuild(BaseTest):
    """Tab 首次进入懒构建渲染正常（nav-POS-003）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_first_visit_tab_renders(self):
        """依次切入未访 Tab，页面应完整渲染（账号入口在屏）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("设备")
        self.userA.go_bottom_tab("我的")
        self.userA.image_exists(SWAN_ME_ACCOUNT_ENTRY, timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
