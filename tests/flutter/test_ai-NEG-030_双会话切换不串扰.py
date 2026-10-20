# CASE-ID: ai-NEG-030
"""Swan 回归·AI 助手域：双会话快速切换 latest-wins 不串扰（ai-NEG-030）。

数据替代说明（执行口径，如实记录）：
- YAML 数据 A-慢回复/B-快回复 为中文，adb 文本注入不可达，以 ASCII 令牌
  A-slow-030 / B-fast-030 等价替代；
- 双会话用双系统角色（小薇/惠威百科）建立——同角色新建会话入口
  （历史页新建聊天）为无文案图标不可锚；
- AI 回复时序（慢/快回复）服务端不可控，断言收敛为 latest-wins 的可观察
  面：各会话仅含自身令牌、往返切换无崩溃无错位无重复。

步骤 → AW 映射：
1. 会话 A 建立并发送 → open_ai_chat_by_role("小薇") + send_chat_text
2. 会话 B 同理（惠威百科）
3. 经历史页按令牌行往返切换 3 轮 → open_ai_history_page + 点令牌行 +
   mixin assert_chat_token（本会话令牌在、对侧令牌不在）

cleanup：无（合成会话留档即本用例产物；零服务端角色写）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestTwoSessionsSwitchNoCrosstalk(SwanRM09Mixin, BaseTest):
    """双会话快速切换回包乱序——latest-wins 不串扰。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_two_sessions_switch_no_crosstalk(self):
        """双会话建立后经历史页往返切换，令牌互不串扰、无崩溃。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")

        # 会话 A：小薇
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text("A-slow-030")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 会话 B：惠威百科
        self.userA.open_ai_chat_by_role("惠威百科")
        self.userA.send_chat_text("B-fast-030")
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

        # 经历史页往返切换 3 轮（A→B→A…），每轮断言会话隔离
        expected = [("A-slow-030", "B-fast-030"), ("B-fast-030", "A-slow-030"),
                    ("A-slow-030", "B-fast-030")]
        for token_in, token_out in expected:
            self.userA.open_ai_history_page()
            self.userA.click_text(token_in, timeout=10)
            self.userA.assert_chat_token(token_in, present=True)
            self.userA.assert_chat_token(token_out, present=False)
            self.userA.press_back()
            self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
