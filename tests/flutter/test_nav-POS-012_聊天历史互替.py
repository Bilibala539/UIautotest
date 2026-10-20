# CASE-ID: nav-POS-012
"""Swan 回归·M03 主框架导航：聊天历史页替换语义不嵌套（nav-POS-012）。

用例 → AW 映射：
- 登录态首页壳 → ensure_logged_in_on_home()；切 AI 聊天页 → go_top_tab("AI")
  + [图] SWAN_AI_CHAT_INPUT 页锚点
- 聊天页 → 历史页 → [OCR] 点击「历史」入口（入口未探索确证，B 类登记
  template_needs）+ [图] SWAN_AI_HISTORY_TITLE 页锚点
- 返回应回到进入聊天前的首页推荐 Tab（替换语义防嵌套）→ press_back() +
  [图] SWAN_HOME_TAB_RECOMMEND_SEL 推荐选中态图断言（选中态图可排除
  仍停在 AI 顶 Tab 的嵌套落点）
- 栈深恒定：重复一轮同链路（AI→历史→返回→推荐选中态）
清理：无（导航壳操作无副作用，冷启动模型自然复位）。
"""
from __future__ import annotations

from conftest import BaseTest
from image.image_name_mapping import (
    SWAN_AI_CHAT_INPUT,
    SWAN_AI_HISTORY_TITLE,
    SWAN_HOME_TAB_RECOMMEND_SEL,
)
from utils.aw.business.swan_r_p01 import SwanRP01Mixin


class TestNavPos012ChatHistoryReplace(SwanRP01Mixin, BaseTest):
    """聊天历史页替换语义不嵌套（nav-POS-012）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_history_page_replaces_chat_no_nesting(self):
        """历史页返回应落首页推荐 Tab 而非聊天页，两轮往返栈深恒定。"""
        self.userA.ensure_logged_in_on_home()
        for _ in range(2):
            self.userA.go_top_tab("AI")
            self.userA.image_exists(SWAN_AI_CHAT_INPUT, timeout=10)
            self.userA.click_text("历史", timeout=10)
            self.userA.image_exists(SWAN_AI_HISTORY_TITLE, timeout=10)
            self.userA.press_back()
            self.userA.image_exists(SWAN_HOME_TAB_RECOMMEND_SEL, timeout=10)

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
