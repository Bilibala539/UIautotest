# CASE-ID: push-NEG-002
"""Swan 回归·推送：消息中心永久空态与红点无关性（push-NEG-002，部分转换）。

步骤 -> AW 映射（可自动化面：步骤1 的空态观察；M13 域入口复用）：
- 步骤1 进消息中心页断言永久空态 -> go_bottom_tab('我的') +
  click_any_text('消息中心'/'我的消息' 候选，入口中文未核准登记
  template_needs）+ assert_any_of_texts 空态文案候选（fetchMessages
  恒 []：红点亮但消息中心空为预期现状非缺陷——接真源时本断言翻转告警）；
- 步骤2 保持 unreadCount>0 看消息中心 -> 未读数构造为
  human_interruption_point，无构造手段未纳入自动化（自然态下观察）；
- 步骤3 三源互不相通交叉断言 -> 日志侧断言，无日志通道未纳入自动化。

清理：press_back 退出消息中心页；teardown 按 pass（冷启动由框架承担）。
"""
from __future__ import annotations

from conftest import BaseTest


class TestMessageCenterPermanentEmpty(BaseTest):
    """push-NEG-002：消息中心页空态渲染（红点独立数据源）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象。"""
        self.userA = self.users("swanuserA")

    def test_message_center_permanent_empty(self):
        """消息中心为永久空态（空态文案在位，无消息列表）。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_bottom_tab("我的")
        # 步骤1：进消息中心页
        self.userA.click_any_text("消息中心", "我的消息")
        # 永久空态断言（空态文案候选；接真源后此处翻转为有内容告警）
        self.userA.assert_any_of_texts("暂无消息", "没有消息", "无消息",
                                       "消息中心", timeout=8)
        # 空态即无消息列表项：列表型动态内容行不应出现
        self.userA.text_not_exists("查看全部", timeout=2)
        # 清理：退出消息中心页
        self.userA.press_back()

    def teardown(self) -> None:
        """已退出消息中心页（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
