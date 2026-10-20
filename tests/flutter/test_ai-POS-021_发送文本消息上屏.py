# CASE-ID: ai-POS-021
"""Swan 回归·AI 助手域：发送文本消息主路径——输入→上屏（ai-POS-021）。

步骤 → AW 映射：
1. 进入角色对话页 → go_top_tab("AI") + mixin open_ai_chat_by_role("小薇")
2-3. 点击输入框输入并点击发送 → mixin send_chat_text：点占位「发送消息」
     聚焦 + input_text + 回车键发送（发送按钮为无文案控件锚未截取，
     见 report.template_needs），断言内容区出现消息气泡文本 + 输入框清空
     回显占位——上屏主路径的可观察状态闭环
4. 发送态反馈 → 退出对话页回 AI 首页（无异常弹窗、页面态正常）

数据说明：YAML「你好，请用一句话介绍你自己」为中文，adb 注入不可达，
以 ASCII 等价文案替代。AI 回复接收由 ai-POS-022 单独覆盖。

cleanup：无（合成会话留档即用例产物；App 冷启动由框架夹具承担）。
"""
from __future__ import annotations

from conftest import BaseTest
from utils.aw.business.swan_r_m09 import SwanRM09Mixin


class TestAiSendTextMessage(SwanRM09Mixin, BaseTest):
    """发送文本消息主路径（输入→上屏）。"""

    def setup(self) -> None:
        """测试前初始化：实例化用户对象（用户信息挂在 userA 上）。"""
        self.userA = self.users("swanuserA")

    def test_send_text_message_echoes(self):
        """输入→发送→气泡上屏→输入框清空主路径闭环。"""
        self.userA.ensure_logged_in_on_home()
        self.userA.go_top_tab("AI")
        self.userA.open_ai_chat_by_role("小薇")
        self.userA.send_chat_text(
            "Hello there, please introduce yourself in one line")

        # 退出对话页（发送态正常、无异常弹窗的页面级可观察面）
        self.userA.press_back()
        self.userA.assert_ai_home_gallery()

    def teardown(self) -> None:
        """无用例私有清理（冷启动模型：App 冷启动由框架夹具承担）。"""
        pass
